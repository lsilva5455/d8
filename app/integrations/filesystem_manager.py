"""
File System Manager for Autonomous Congress
Provides safe access to local files and GitHub integration
"""

import os
import logging
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class FileSystemManager:
    """
    Manages file system operations for Congress
    
    Provides:
    - Safe read/write access to project files
    - Directory browsing
    - File search
    - Git operations (commit, push, PR)
    - Backup/rollback capabilities
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize file system manager
        
        Args:
            github_token: GitHub token for PR operations
        """
        self.project_root = Path("c:/Users/PcDos/d8")
        self.data_root = Path.home() / "Documents" / "d8_data"
        
        # Allowed paths for safety
        self.allowed_paths = [
            self.project_root,
            self.data_root
        ]
        
        # GitHub integration
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.repo_owner = os.getenv("GITHUB_REPO_OWNER", "lsilva5455")
        self.repo_name = os.getenv("GITHUB_REPO_NAME", "d8")
        self.branch = os.getenv("GITHUB_REPO_BRANCH", "docker-workers")
        
        # Backup directory
        self.backup_dir = self.data_root / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📁 FileSystemManager initialized")
        logger.info(f"   Project root: {self.project_root}")
        logger.info(f"   Data root: {self.data_root}")
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is within allowed directories"""
        path = path.resolve()
        return any(
            str(path).startswith(str(allowed.resolve()))
            for allowed in self.allowed_paths
        )
    
    def _validate_path(self, path: str) -> Path:
        """
        Validate and resolve path
        
        Args:
            path: Path to validate (can be relative or absolute)
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If path is not allowed
        """
        # Convert to Path
        if path.startswith("~/Documents/d8_data"):
            path_obj = Path(path.replace("~/Documents/d8_data", str(self.data_root)))
        elif path.startswith("~/d8"):
            path_obj = Path(path.replace("~/d8", str(self.project_root)))
        elif path.startswith("d8/"):
            path_obj = self.project_root / path[3:]
        else:
            path_obj = Path(path)
        
        # Resolve to absolute
        if not path_obj.is_absolute():
            path_obj = self.project_root / path_obj
        
        path_obj = path_obj.resolve()
        
        # Check if allowed
        if not self._is_path_allowed(path_obj):
            raise ValueError(
                f"Access denied: {path_obj} is outside allowed directories"
            )
        
        return path_obj
    
    def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """
        List contents of a directory
        
        Args:
            path: Directory path (relative to project root or absolute)
            
        Returns:
            {
                "path": str,
                "files": [...],
                "directories": [...]
            }
        """
        try:
            dir_path = self._validate_path(path)
            
            if not dir_path.exists():
                return {"error": f"Directory not found: {path}"}
            
            if not dir_path.is_dir():
                return {"error": f"Not a directory: {path}"}
            
            files = []
            directories = []
            
            for item in dir_path.iterdir():
                if item.is_file():
                    files.append({
                        "name": item.name,
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
                elif item.is_dir():
                    directories.append(item.name)
            
            return {
                "path": str(dir_path),
                "files": files,
                "directories": directories
            }
            
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            return {"error": str(e)}
    
    def read_file(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        Read file contents
        
        Args:
            path: File path
            encoding: File encoding (default: utf-8)
            
        Returns:
            {
                "path": str,
                "content": str,
                "size": int,
                "lines": int
            }
        """
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return {"error": f"File not found: {path}"}
            
            if not file_path.is_file():
                return {"error": f"Not a file: {path}"}
            
            content = file_path.read_text(encoding=encoding)
            lines = content.split('\n')
            
            return {
                "path": str(file_path),
                "content": content,
                "size": file_path.stat().st_size,
                "lines": len(lines)
            }
            
        except Exception as e:
            logger.error(f"Error reading file {path}: {e}")
            return {"error": str(e)}
    
    def write_file(
        self,
        path: str,
        content: str,
        create_backup: bool = True,
        encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """
        Write content to file
        
        Args:
            path: File path
            content: Content to write
            create_backup: Create backup before writing
            encoding: File encoding
            
        Returns:
            {
                "path": str,
                "backup_path": str (if backup created),
                "bytes_written": int
            }
        """
        try:
            file_path = self._validate_path(path)
            
            # Create backup if file exists
            backup_path = None
            if create_backup and file_path.exists():
                backup_path = self._create_backup(file_path)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            file_path.write_text(content, encoding=encoding)
            
            result = {
                "path": str(file_path),
                "bytes_written": len(content.encode(encoding))
            }
            
            if backup_path:
                result["backup_path"] = str(backup_path)
            
            logger.info(f"✅ Wrote {result['bytes_written']} bytes to {file_path.name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error writing file {path}: {e}")
            return {"error": str(e)}
    
    def _create_backup(self, file_path: Path) -> Path:
        """Create backup of file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        backup_path.write_bytes(file_path.read_bytes())
        logger.info(f"💾 Backup created: {backup_path.name}")
        
        return backup_path
    
    def search_files(
        self,
        pattern: str,
        path: str = ".",
        case_sensitive: bool = False
    ) -> List[str]:
        """
        Search for files matching pattern
        
        Args:
            pattern: Filename pattern (e.g., "*.py", "test_*")
            path: Directory to search in
            case_sensitive: Case-sensitive search
            
        Returns:
            List of matching file paths
        """
        try:
            search_path = self._validate_path(path)
            
            if not search_path.exists():
                return []
            
            if case_sensitive:
                matches = list(search_path.rglob(pattern))
            else:
                # Case-insensitive search
                matches = [
                    f for f in search_path.rglob("*")
                    if f.is_file() and pattern.lower() in f.name.lower()
                ]
            
            # Return relative paths
            return [
                str(m.relative_to(self.project_root))
                if str(m).startswith(str(self.project_root))
                else str(m.relative_to(self.data_root))
                for m in matches
            ]
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            return []
    
    def git_status(self) -> Dict[str, Any]:
        """
        Get git status of project
        
        Returns:
            {
                "branch": str,
                "modified": [...],
                "untracked": [...],
                "staged": [...]
            }
        """
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain", "--branch"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": result.stderr}
            
            lines = result.stdout.strip().split('\n')
            branch = lines[0].replace("## ", "") if lines else "unknown"
            
            modified = []
            untracked = []
            staged = []
            
            for line in lines[1:]:
                if not line:
                    continue
                
                status = line[:2]
                filename = line[3:].strip()
                
                if status.startswith('?'):
                    untracked.append(filename)
                elif status.startswith('M'):
                    modified.append(filename)
                elif status.startswith('A'):
                    staged.append(filename)
            
            return {
                "branch": branch,
                "modified": modified,
                "untracked": untracked,
                "staged": staged
            }
            
        except Exception as e:
            logger.error(f"Error getting git status: {e}")
            return {"error": str(e)}
    
    def git_commit(
        self,
        files: List[str],
        message: str,
        author_name: str = "D8 Autonomous Congress",
        author_email: str = "congress@d8.ai"
    ) -> Dict[str, Any]:
        """
        Commit changes to git
        
        Args:
            files: List of files to commit
            message: Commit message
            author_name: Author name
            author_email: Author email
            
        Returns:
            {
                "success": bool,
                "commit_hash": str,
                "message": str
            }
        """
        try:
            # Stage files
            for file in files:
                result = subprocess.run(
                    ["git", "add", file],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return {"error": f"Failed to stage {file}: {result.stderr}"}
            
            # Commit
            result = subprocess.run(
                [
                    "git", "commit",
                    "-m", message,
                    f"--author={author_name} <{author_email}>"
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": f"Commit failed: {result.stderr}"}
            
            # Get commit hash
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            commit_hash = result.stdout.strip()
            
            logger.info(f"✅ Committed changes: {commit_hash[:8]}")
            
            return {
                "success": True,
                "commit_hash": commit_hash,
                "message": message
            }
            
        except Exception as e:
            logger.error(f"Error committing: {e}")
            return {"error": str(e)}
    
    def create_pull_request(
        self,
        title: str,
        body: str,
        head_branch: Optional[str] = None,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create pull request on GitHub
        
        Args:
            title: PR title
            body: PR description
            head_branch: Source branch (default: current branch)
            base_branch: Target branch
            
        Returns:
            {
                "success": bool,
                "pr_number": int,
                "pr_url": str
            }
        """
        if not self.github_token:
            return {"error": "GITHUB_TOKEN not configured"}
        
        try:
            # Get current branch if not specified
            if not head_branch:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                head_branch = result.stdout.strip()
            
            # Create PR via GitHub API
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/pulls"
            
            headers = {
                "Authorization": f"Bearer {self.github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }
            
            data = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code != 201:
                return {
                    "error": f"Failed to create PR: {response.status_code}",
                    "details": response.json()
                }
            
            pr_data = response.json()
            
            logger.info(f"✅ Created PR #{pr_data['number']}: {title}")
            
            return {
                "success": True,
                "pr_number": pr_data["number"],
                "pr_url": pr_data["html_url"],
                "state": pr_data["state"]
            }
            
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return {"error": str(e)}
    
    def push_to_github(self, branch: Optional[str] = None) -> Dict[str, Any]:
        """
        Push commits to GitHub
        
        Args:
            branch: Branch to push (default: current branch)
            
        Returns:
            {"success": bool, "message": str}
        """
        try:
            if not branch:
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True
                )
                branch = result.stdout.strip()
            
            result = subprocess.run(
                ["git", "push", "origin", branch],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": f"Push failed: {result.stderr}"}
            
            logger.info(f"✅ Pushed to origin/{branch}")
            
            return {
                "success": True,
                "message": f"Pushed to origin/{branch}"
            }
            
        except Exception as e:
            logger.error(f"Error pushing: {e}")
            return {"error": str(e)}


def get_filesystem_manager() -> Optional[FileSystemManager]:
    """Get singleton FileSystemManager instance"""
    return FileSystemManager()
