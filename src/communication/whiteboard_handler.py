"""
Whiteboard Handler for canvas drawing and snapshot management.

This module provides the WhiteboardHandler class for managing whiteboard
canvas operations including drawing, saving snapshots, and clearing.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.exceptions import CommunicationError


class WhiteboardHandler:
    """
    Handles whiteboard canvas operations and snapshot management.
    
    Integrates with streamlit-drawable-canvas for drawing system diagrams
    and manages snapshot storage.
    """

    def __init__(
        self,
        file_storage,
        logger=None,
        canvas_width: int = 800,
        canvas_height: int = 600,
        image_format: str = "png"
    ):
        """
        Initialize whiteboard handler.
        
        Args:
            file_storage: FileStorage instance for saving whiteboard snapshots
            logger: LoggingManager instance for logging
            canvas_width: Canvas width in pixels (default: 800)
            canvas_height: Canvas height in pixels (default: 600)
            image_format: Image format for snapshots (default: png)
        """
        self.file_storage = file_storage
        self.logger = logger
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.image_format = image_format
        
        # Track snapshots per session
        self._session_snapshots: Dict[str, List[str]] = {}
        
        if self.logger:
            self.logger.info(
                component="WhiteboardHandler",
                operation="initialize",
                message="Whiteboard handler initialized",
                metadata={
                    "canvas_width": canvas_width,
                    "canvas_height": canvas_height,
                    "format": image_format
                }
            )

    def save_whiteboard(
        self,
        session_id: str,
        canvas_data: bytes,
        snapshot_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save whiteboard canvas snapshot.
        
        Args:
            session_id: Session identifier
            canvas_data: Canvas image data as bytes
            snapshot_number: Optional snapshot number for ordering
            metadata: Optional metadata (e.g., timestamp, description)
            
        Returns:
            Relative file path to saved snapshot
            
        Raises:
            CommunicationError: If saving snapshot fails
        """
        try:
            if self.logger:
                self.logger.debug(
                    component="WhiteboardHandler",
                    operation="save_whiteboard",
                    message=f"Saving whiteboard snapshot for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "canvas_size_bytes": len(canvas_data),
                        "snapshot_number": snapshot_number
                    }
                )
            
            # Prepare metadata
            save_metadata = {
                "canvas_width": self.canvas_width,
                "canvas_height": self.canvas_height,
                "timestamp": datetime.now().isoformat()
            }
            if snapshot_number is not None:
                save_metadata["snapshot_number"] = snapshot_number
            if metadata:
                save_metadata.update(metadata)
            
            # Save snapshot
            file_path = self.file_storage.save_whiteboard(
                session_id=session_id,
                canvas_data=canvas_data,
                format=self.image_format,
                metadata=save_metadata
            )
            
            # Track snapshot for this session
            if session_id not in self._session_snapshots:
                self._session_snapshots[session_id] = []
            self._session_snapshots[session_id].append(file_path)
            
            if self.logger:
                self.logger.info(
                    component="WhiteboardHandler",
                    operation="save_whiteboard",
                    message=f"Whiteboard snapshot saved for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "file_path": file_path,
                        "snapshot_count": len(self._session_snapshots[session_id])
                    }
                )
            
            return file_path
            
        except Exception as e:
            error_msg = f"Failed to save whiteboard snapshot for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="WhiteboardHandler",
                    operation="save_whiteboard",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def clear_canvas(self, session_id: str) -> None:
        """
        Clear the whiteboard canvas for a session.
        
        This is a logical operation that marks the canvas as cleared.
        The actual canvas clearing is handled by the UI component.
        
        Args:
            session_id: Session identifier
        """
        if self.logger:
            self.logger.info(
                component="WhiteboardHandler",
                operation="clear_canvas",
                message=f"Canvas cleared for session {session_id}",
                session_id=session_id
            )

    def get_snapshot_count(self, session_id: str) -> int:
        """
        Get the number of snapshots saved for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Number of snapshots
        """
        return len(self._session_snapshots.get(session_id, []))

    def get_snapshots(self, session_id: str) -> List[str]:
        """
        Get all snapshot file paths for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of snapshot file paths
        """
        return self._session_snapshots.get(session_id, []).copy()

    def get_latest_snapshot(self, session_id: str) -> Optional[str]:
        """
        Get the most recent snapshot for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            File path to latest snapshot or None if no snapshots
        """
        snapshots = self._session_snapshots.get(session_id, [])
        return snapshots[-1] if snapshots else None

    def delete_snapshot(self, session_id: str, file_path: str) -> bool:
        """
        Delete a specific snapshot.
        
        Args:
            session_id: Session identifier
            file_path: Path to snapshot file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if session_id not in self._session_snapshots:
                return False
            
            if file_path not in self._session_snapshots[session_id]:
                return False
            
            # Remove from tracking
            self._session_snapshots[session_id].remove(file_path)
            
            # Delete file from filesystem
            abs_path = self.file_storage.get_file_path(file_path)
            if abs_path.exists():
                abs_path.unlink()
            
            if self.logger:
                self.logger.info(
                    component="WhiteboardHandler",
                    operation="delete_snapshot",
                    message=f"Deleted snapshot for session {session_id}",
                    session_id=session_id,
                    metadata={"file_path": file_path}
                )
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="WhiteboardHandler",
                    operation="delete_snapshot",
                    message=f"Failed to delete snapshot: {e}",
                    session_id=session_id,
                    exc_info=e
                )
            return False

    def auto_save_snapshot(
        self,
        session_id: str,
        canvas_data: bytes,
        interval_seconds: int = 60
    ) -> Optional[str]:
        """
        Auto-save a snapshot at regular intervals.
        
        Args:
            session_id: Session identifier
            canvas_data: Canvas image data as bytes
            interval_seconds: Interval for auto-save (default: 60)
            
        Returns:
            File path to saved snapshot or None if not saved
        """
        try:
            # Get current snapshot count
            snapshot_count = self.get_snapshot_count(session_id)
            
            # Save with auto-save metadata
            file_path = self.save_whiteboard(
                session_id=session_id,
                canvas_data=canvas_data,
                snapshot_number=snapshot_count + 1,
                metadata={
                    "auto_save": True,
                    "interval_seconds": interval_seconds
                }
            )
            
            return file_path
            
        except Exception as e:
            if self.logger:
                self.logger.error(
                    component="WhiteboardHandler",
                    operation="auto_save_snapshot",
                    message=f"Auto-save failed for session {session_id}: {e}",
                    session_id=session_id,
                    exc_info=e
                )
            return None

    def export_snapshots(
        self,
        session_id: str,
        export_dir: Optional[str] = None
    ) -> List[str]:
        """
        Export all snapshots for a session to a directory.
        
        Args:
            session_id: Session identifier
            export_dir: Optional export directory (default: session directory)
            
        Returns:
            List of exported file paths
            
        Raises:
            CommunicationError: If export fails
        """
        try:
            snapshots = self.get_snapshots(session_id)
            
            if not snapshots:
                if self.logger:
                    self.logger.warning(
                        component="WhiteboardHandler",
                        operation="export_snapshots",
                        message=f"No snapshots to export for session {session_id}",
                        session_id=session_id
                    )
                return []
            
            # Determine export directory
            if export_dir:
                export_path = Path(export_dir)
            else:
                export_path = self.file_storage.base_dir / session_id / "whiteboard_export"
            
            export_path.mkdir(parents=True, exist_ok=True)
            
            exported_files = []
            for i, snapshot_path in enumerate(snapshots, 1):
                # Copy snapshot to export directory
                src_path = self.file_storage.get_file_path(snapshot_path)
                dst_path = export_path / f"snapshot_{i:03d}.{self.image_format}"
                
                if src_path.exists():
                    import shutil
                    shutil.copy2(src_path, dst_path)
                    exported_files.append(str(dst_path))
            
            if self.logger:
                self.logger.info(
                    component="WhiteboardHandler",
                    operation="export_snapshots",
                    message=f"Exported {len(exported_files)} snapshots for session {session_id}",
                    session_id=session_id,
                    metadata={
                        "export_dir": str(export_path),
                        "snapshot_count": len(exported_files)
                    }
                )
            
            return exported_files
            
        except Exception as e:
            error_msg = f"Failed to export snapshots for session {session_id}: {e}"
            if self.logger:
                self.logger.error(
                    component="WhiteboardHandler",
                    operation="export_snapshots",
                    message=error_msg,
                    session_id=session_id,
                    exc_info=e
                )
            raise CommunicationError(error_msg)

    def get_canvas_config(self) -> Dict[str, Any]:
        """
        Get canvas configuration for UI rendering.
        
        Returns:
            Dictionary with canvas configuration
        """
        return {
            "width": self.canvas_width,
            "height": self.canvas_height,
            "format": self.image_format,
            "drawing_modes": ["freedraw", "line", "rect", "circle", "transform"],
            "default_stroke_width": 2,
            "default_stroke_color": "#000000",
            "background_color": "#ffffff"
        }
