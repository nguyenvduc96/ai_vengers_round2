"""
Session Manager for maintaining context across image generations
Enables character consistency and multi-step workflows
"""


import json
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from uuid import uuid4


from config import (
   DEFAULT_SESSIONS_DIR,
   SESSION_ID_LENGTH,
   SessionConfig
)




class Session:
   """Represents a generation session with history and context"""
  
   def __init__(
       self,
       session_id: str,
       config: Optional[SessionConfig] = None,
       session_dir: str = DEFAULT_SESSIONS_DIR
   ):
       """
       Initialize a session
      
       Args:
           session_id: Unique session identifier
           config: Session configuration
           session_dir: Base directory for sessions
       """
       self.session_id = session_id
       self.config = config or SessionConfig()
       self.session_dir = session_dir
       self.session_path = os.path.join(session_dir, session_id)
      
       # Session data
       self.messages: List[Dict[str, Any]] = []
       self.generated_images: List[str] = []
       self.reference_images: List[str] = []
       self.metadata: Dict[str, Any] = {
           "created_at": datetime.now().isoformat(),
           "last_updated": datetime.now().isoformat(),
           "generation_count": 0
       }
      
       # Create session directory
       os.makedirs(self.session_path, exist_ok=True)
       os.makedirs(os.path.join(self.session_path, "images"), exist_ok=True)
       os.makedirs(os.path.join(self.session_path, "references"), exist_ok=True)
  
   def add_message(self, role: str, content: str):
       """Add message to conversation history"""
       message = {
           "role": role,
           "content": content,
           "timestamp": datetime.now().isoformat()
       }
       self.messages.append(message)
      
       # Trim history if needed
       if len(self.messages) > self.config.max_history * 2:  # *2 for user+assistant pairs
           self.messages = self.messages[-(self.config.max_history * 2):]
      
       self.metadata["last_updated"] = datetime.now().isoformat()
  
   def add_generated_image(self, image_path: str, copy_to_session: bool = True) -> str:
       """
       Add generated image to session
      
       Args:
           image_path: Path to generated image
           copy_to_session: Whether to copy image to session folder
          
       Returns:
           Path to image (in session folder if copied)
       """
       if copy_to_session:
           # Copy to session images folder
           filename = os.path.basename(image_path)
           session_image_path = os.path.join(self.session_path, "images", filename)
           shutil.copy2(image_path, session_image_path)
           self.generated_images.append(session_image_path)
           return session_image_path
       else:
           self.generated_images.append(image_path)
           return image_path
  
   def add_reference_image(self, image_path: str) -> str:
       """
       Add reference image to session
      
       Args:
           image_path: Path to reference image
          
       Returns:
           Path to image in session references folder
       """
       if self.config.save_references:
           # Copy to session references folder
           filename = os.path.basename(image_path)
           timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
           session_ref_path = os.path.join(
               self.session_path,
               "references",
               f"{timestamp}_{filename}"
           )
           shutil.copy2(image_path, session_ref_path)
           self.reference_images.append(session_ref_path)
           return session_ref_path
       else:
           self.reference_images.append(image_path)
           return image_path
  
   def get_messages_for_api(self) -> List[Dict[str, str]]:
       """
       Get messages formatted for API
      
       Returns:
           List of message dicts with role and content
       """
       return [
           {"role": msg["role"], "content": msg["content"]}
           for msg in self.messages
       ]
  
   def get_latest_generated_image(self) -> Optional[str]:
       """Get path to most recently generated image"""
       return self.generated_images[-1] if self.generated_images else None
  
   def increment_generation_count(self):
       """Increment generation counter"""
       self.metadata["generation_count"] += 1
       self.metadata["last_updated"] = datetime.now().isoformat()
  
   def save(self):
       """Save session data to disk"""
       session_data = {
           "session_id": self.session_id,
           "messages": self.messages,
           "generated_images": self.generated_images,
           "reference_images": self.reference_images,
           "metadata": self.metadata,
           "config": {
               "max_history": self.config.max_history,
               "save_references": self.config.save_references,
               "auto_cleanup": self.config.auto_cleanup,
               "timeout_hours": self.config.timeout_hours
           }
       }
      
       session_file = os.path.join(self.session_path, "session.json")
       with open(session_file, 'w') as f:
           json.dump(session_data, f, indent=2)
  
   @classmethod
   def load(cls, session_id: str, session_dir: str = DEFAULT_SESSIONS_DIR) -> 'Session':
       """
       Load session from disk
      
       Args:
           session_id: Session identifier
           session_dir: Base directory for sessions
          
       Returns:
           Loaded Session object
       """
       session_path = os.path.join(session_dir, session_id)
       session_file = os.path.join(session_path, "session.json")
      
       if not os.path.exists(session_file):
           raise FileNotFoundError(f"Session not found: {session_id}")
      
       with open(session_file, 'r') as f:
           data = json.load(f)
      
       # Recreate config
       config_data = data.get("config", {})
       config = SessionConfig(**config_data)
      
       # Create session
       session = cls(session_id, config, session_dir)
       session.messages = data.get("messages", [])
       session.generated_images = data.get("generated_images", [])
       session.reference_images = data.get("reference_images", [])
       session.metadata = data.get("metadata", session.metadata)
      
       return session
  
   def get_summary(self) -> Dict[str, Any]:
       """Get session summary"""
       return {
           "session_id": self.session_id,
           "created_at": self.metadata.get("created_at"),
           "last_updated": self.metadata.get("last_updated"),
           "generation_count": self.metadata.get("generation_count", 0),
           "message_count": len(self.messages),
           "generated_images_count": len(self.generated_images),
           "reference_images_count": len(self.reference_images),
           "session_path": self.session_path
       }




class SessionManager:
   """Manages multiple sessions"""
  
   def __init__(self, session_dir: str = DEFAULT_SESSIONS_DIR):
       """
       Initialize session manager
      
       Args:
           session_dir: Base directory for sessions
       """
       self.session_dir = session_dir
       os.makedirs(session_dir, exist_ok=True)
  
   def create_session(
       self,
       session_id: Optional[str] = None,
       config: Optional[SessionConfig] = None
   ) -> Session:
       """
       Create new session
      
       Args:
           session_id: Optional custom session ID
           config: Optional session configuration
          
       Returns:
           New Session object
       """
       if session_id is None:
           # Generate unique session ID
           session_id = str(uuid4())[:SESSION_ID_LENGTH]
      
       session = Session(session_id, config, self.session_dir)
       session.save()
      
       return session
  
   def load_session(self, session_id: str) -> Session:
       """
       Load existing session
      
       Args:
           session_id: Session identifier
          
       Returns:
           Loaded Session object
       """
       return Session.load(session_id, self.session_dir)
  
   def list_sessions(self) -> List[Dict[str, Any]]:
       """
       List all available sessions
      
       Returns:
           List of session summaries
       """
       sessions = []
      
       if not os.path.exists(self.session_dir):
           return sessions
      
       for session_id in os.listdir(self.session_dir):
           session_path = os.path.join(self.session_dir, session_id)
           session_file = os.path.join(session_path, "session.json")
          
           if os.path.isdir(session_path) and os.path.exists(session_file):
               try:
                   session = self.load_session(session_id)
                   sessions.append(session.get_summary())
               except Exception:
                   continue
      
       # Sort by last updated
       sessions.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
      
       return sessions
  
   def delete_session(self, session_id: str):
       """
       Delete session and all associated files
      
       Args:
           session_id: Session identifier
       """
       session_path = os.path.join(self.session_dir, session_id)
      
       if os.path.exists(session_path):
           shutil.rmtree(session_path)
  
   def cleanup_old_sessions(self, hours: int = 24):
       """
       Delete sessions older than specified hours
      
       Args:
           hours: Age threshold in hours
       """
       cutoff_time = datetime.now() - timedelta(hours=hours)
       deleted_count = 0
      
       for session_summary in self.list_sessions():
           last_updated_str = session_summary.get("last_updated")
           if last_updated_str:
               last_updated = datetime.fromisoformat(last_updated_str)
               if last_updated < cutoff_time:
                   self.delete_session(session_summary["session_id"])
                   deleted_count += 1
      
       return deleted_count
  
   def get_session_count(self) -> int:
       """Get total number of sessions"""
       return len(self.list_sessions())






