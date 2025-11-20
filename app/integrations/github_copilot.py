"""
GitHub Copilot Integration for Intelligent Bot Responses

This module integrates GitHub Copilot API to give the Telegram bot
deep understanding of the D8 project structure, code, and context.
"""

import os
import logging
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class GitHubCopilotClient:
    """
    Client for GitHub Copilot API
    
    Provides intelligent code understanding and context-aware responses
    by querying the project repository through GitHub's API.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub Copilot client
        
        Args:
            github_token: GitHub Personal Access Token with Copilot access
        """
        self.token = github_token or os.getenv("GITHUB_TOKEN")
        
        if not self.token:
            logger.warning("⚠️  GITHUB_TOKEN not found. Bot will have limited intelligence.")
            self.enabled = False
            return
        
        self.enabled = True
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Project context
        self.repo_owner = "lsilva5455"
        self.repo_name = "d8"
        self.project_root = Path(__file__).parent.parent.parent
        
        logger.info(f"🧠 GitHub Copilot client initialized for {self.repo_owner}/{self.repo_name}")
    
    def get_project_context(self) -> Dict[str, Any]:
        """
        Get comprehensive project context from repository
        
        Returns:
            Dict with project structure, key files, and documentation
        """
        if not self.enabled:
            return {"error": "GitHub integration disabled"}
        
        try:
            context = {
                "structure": self._get_repo_structure(),
                "key_files": self._get_key_files(),
                "documentation": self._get_documentation(),
                "recent_commits": self._get_recent_commits(limit=5)
            }
            return context
            
        except Exception as e:
            logger.error(f"Error getting project context: {e}")
            return {"error": str(e)}
    
    def _get_repo_structure(self) -> Dict[str, Any]:
        """Get repository tree structure"""
        try:
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/git/trees/docker-workers?recursive=1"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                tree = response.json().get("tree", [])
                
                # Organize by directory
                structure = {}
                for item in tree:
                    path = item["path"]
                    if "/" in path:
                        dir_name = path.split("/")[0]
                        if dir_name not in structure:
                            structure[dir_name] = []
                        structure[dir_name].append(path)
                
                return structure
            else:
                logger.warning(f"Failed to get repo structure: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting repo structure: {e}")
            return {}
    
    def _get_key_files(self) -> Dict[str, str]:
        """Get content of key project files"""
        key_files = [
            "docs/01_arquitectura/VISION_COMPLETA_D8.md",
            "docs/01_arquitectura/ROADMAP_7_FASES.md",
            "PENDIENTES.md",
            "README.md",
            "docs/06_knowledge_base/experiencias_profundas/congreso_autonomo.md"
        ]
        
        content = {}
        for file_path in key_files:
            try:
                url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}?ref=docker-workers"
                response = requests.get(url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    import base64
                    file_data = response.json()
                    content[file_path] = base64.b64decode(file_data["content"]).decode('utf-8')
                    
            except Exception as e:
                logger.error(f"Error getting {file_path}: {e}")
                continue
        
        return content
    
    def _get_documentation(self) -> List[str]:
        """List all documentation files"""
        try:
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/docs?ref=docker-workers"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                docs = response.json()
                return [doc["name"] for doc in docs if doc["type"] == "dir"]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting documentation: {e}")
            return []
    
    def _get_recent_commits(self, limit: int = 5) -> List[Dict[str, str]]:
        """Get recent commit messages for context"""
        try:
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits?sha=docker-workers&per_page={limit}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                commits = response.json()
                return [
                    {
                        "message": commit["commit"]["message"],
                        "author": commit["commit"]["author"]["name"],
                        "date": commit["commit"]["author"]["date"]
                    }
                    for commit in commits
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error getting recent commits: {e}")
            return []
    
    def ask_about_project(self, question: str) -> str:
        """
        Ask intelligent question about the project
        
        Strategy:
        1. Try GitHub Copilot API first (has repo context)
        2. If fails, fallback to Groq with project context
        
        Args:
            question: User's question about the project
            
        Returns:
            Intelligent response with project context
        """
        if not self.enabled:
            logger.warning("GitHub integration disabled, using Groq with project context")
            return self._ask_with_groq(question)
        
        try:
            # Try GitHub Copilot API first
            response = self._ask_github_copilot(question)
            if response:
                return response
                
        except Exception as e:
            logger.warning(f"GitHub Copilot failed: {e}, falling back to Groq")
        
        # Fallback to Groq with project context
        return self._ask_with_groq(question)
    
    def _ask_github_copilot(self, question: str) -> Optional[str]:
        """
        Ask GitHub Copilot API directly (if available)
        
        Note: GitHub Copilot API for chat is still in beta.
        This is a placeholder for when it becomes available.
        """
        # GitHub Copilot Chat API is not yet publicly available
        # When it becomes available, implement here
        logger.debug("GitHub Copilot Chat API not yet available, using Groq with context")
        return None
    
    def _ask_with_groq(self, question: str) -> str:
        """
        Ask using Groq with GitHub project context
        
        This gives intelligent responses by loading project documentation
        and code structure from GitHub API.
        """
        try:
            # Get project context from GitHub
            context = self.get_project_context()
            
            # Build intelligent prompt with context
            prompt = self._build_contextual_prompt(question, context)
            
            # Use Groq for response
            from app.integrations.groq_client import GroqClient
            groq = GroqClient(
                api_key=os.getenv("GROQ_API_KEY"),
                model="llama-3.3-70b-versatile"  # Latest available model
            )
            
            response = groq.chat(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                json_mode=False  # Plain text response
            )
            
            return response["content"]
            
        except Exception as e:
            logger.error(f"Error asking with Groq: {e}")
            return f"Lo siento, tuve un problema procesando tu pregunta. Error: {str(e)[:100]}"
    
    def _build_contextual_prompt(self, question: str, context: Dict[str, Any]) -> str:
        """Build prompt with full project context"""
        
        # Extract key documentation
        vision = context.get("key_files", {}).get("docs/01_arquitectura/VISION_COMPLETA_D8.md", "")[:5000]
        roadmap = context.get("key_files", {}).get("docs/01_arquitectura/ROADMAP_7_FASES.md", "")[:5000]
        pendientes = context.get("key_files", {}).get("PENDIENTES.md", "")[:3000]
        
        prompt = f"""Eres un experto en el proyecto D8 con conocimiento completo del código y arquitectura.

# CONTEXTO DEL PROYECTO D8

## Visión General
{vision[:2000] if vision else "D8 es un sistema autónomo de agentes de IA que mejora continuamente sin intervención humana."}

## Roadmap
{roadmap[:2000] if roadmap else "Sistema en 7 fases desde economia mock hasta autonomía total."}

## Estado Actual
{pendientes[:1000] if pendientes else "Ver PENDIENTES.md para detalles."}

## Estructura del Proyecto
- app/ - Lógica específica de D8
  - agents/ - Implementaciones de agentes
  - evolution/ - Algoritmos genéticos
  - congress/ - Sistema de mejora continua
  - economy/ - Sistema económico D8 Credits
  - integrations/ - APIs externas (Groq, Gemini, Telegram)
  
- lib/ - Utilidades reutilizables
  - llm/ - Clientes LLM (Groq, Gemini, DeepSeek)
  - validation/ - Schemas Pydantic
  - parsers/ - Procesamiento de texto

- scripts/ - Scripts ejecutables
  - autonomous_congress.py - Congreso autónomo
  - launch_congress_telegram.py - Bot Telegram
  - niche_discovery_agent.py - Descubrimiento de nichos

- docs/ - Documentación completa
  - 01_arquitectura/ - Visión y diseño
  - 03_operaciones/ - Guías de uso
  - 06_knowledge_base/ - Conocimiento acumulado

## Principios Fundamentales
1. Autonomía total - Cero intervención humana después de setup
2. Mejora continua - Congreso experimenta y evoluciona el sistema
3. Economía autónoma - D8 Credits, revenue attribution 40/40/20
4. 6 Leyes Fundamentales en blockchain (solo Leo puede modificar)

## Sistemas Clave
- Darwin (Evolución): Selección natural de agentes via fitness
- Congress (Mejora): Investiga, experimenta, valida, implementa
- Niche Discovery: Descubre nichos rentables automáticamente
- Economy: D8 Credits (BEP-20), accounting autónomo, revenue attribution

IMPORTANTE: Responde de forma clara y directa en texto plano. NO uses Markdown, NO uses asteriscos, NO uses guiones bajos. Solo texto simple y claro. 

Responde la pregunta del usuario con este contexto completo. Sé conciso pero preciso (máximo 500 palabras). Si no sabes algo, dilo honestamente."""

        return prompt
    
    def search_code(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search code in repository
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            List of code snippets matching query
        """
        if not self.enabled:
            return []
        
        try:
            url = f"{self.base_url}/search/code"
            params = {
                "q": f"{query} repo:{self.repo_owner}/{self.repo_name}",
                "per_page": max_results
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                results = response.json().get("items", [])
                return [
                    {
                        "path": item["path"],
                        "name": item["name"],
                        "url": item["html_url"]
                    }
                    for item in results
                ]
            
            return []
            
        except Exception as e:
            logger.error(f"Error searching code: {e}")
            return []
    
    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Get content of specific file from repository
        
        Args:
            file_path: Path to file in repository
            
        Returns:
            File content as string
        """
        if not self.enabled:
            return None
        
        try:
            url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}?ref=docker-workers"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                import base64
                file_data = response.json()
                return base64.b64decode(file_data["content"]).decode('utf-8')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file content: {e}")
            return None


# Singleton instance
_copilot_client = None

def get_copilot_client() -> GitHubCopilotClient:
    """Get or create singleton Copilot client"""
    global _copilot_client
    if _copilot_client is None:
        _copilot_client = GitHubCopilotClient()
    return _copilot_client
