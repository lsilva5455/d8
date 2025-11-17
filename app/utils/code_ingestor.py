"""
Code Ingestor - AST-based Legacy Code Parser
Extracts functions and classes from Python files for RAG system
"""

import ast
import os
import hashlib
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeFragment:
    """Represents a parsed code fragment (function or class)"""
    type: str  # 'function', 'class', 'method'
    name: str
    source_code: str
    docstring: Optional[str]
    file_path: str
    line_start: int
    line_end: int
    signature: str  # Function/method signature
    dependencies: List[str]  # Imported modules
    metadata: Dict[str, Any]  # Custom metadata (platform, action, etc.)
    hash: str  # Unique identifier
    
    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.md5(
                f"{self.file_path}:{self.name}:{self.line_start}".encode()
            ).hexdigest()


class ASTCodeParser:
    """Parse Python code using AST to extract semantic units"""
    
    def __init__(self):
        self.fragments: List[CodeFragment] = []
    
    def parse_file(self, file_path: str) -> List[CodeFragment]:
        """
        Parse a Python file and extract all functions and classes
        
        Returns:
            List of CodeFragment objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=file_path)
            
            # Extract imports for dependency tracking
            imports = self._extract_imports(tree)
            
            fragments = []
            
            # Extract top-level functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    fragment = self._parse_function(node, source, file_path, imports)
                    if fragment:
                        fragments.append(fragment)
                
                elif isinstance(node, ast.ClassDef):
                    class_fragment = self._parse_class(node, source, file_path, imports)
                    if class_fragment:
                        fragments.append(class_fragment)
                    
                    # Extract methods from class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_fragment = self._parse_method(
                                item, node.name, source, file_path, imports
                            )
                            if method_fragment:
                                fragments.append(method_fragment)
            
            logger.info(f"✅ Parsed {file_path}: {len(fragments)} fragments extracted")
            return fragments
            
        except SyntaxError as e:
            logger.error(f"❌ Syntax error in {file_path}: {e}")
            return []
        except Exception as e:
            logger.error(f"❌ Failed to parse {file_path}: {e}")
            return []
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extract all import statements"""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        return imports
    
    def _get_source_segment(self, source: str, node: ast.AST) -> str:
        """Extract source code for a specific AST node"""
        lines = source.split('\n')
        start_line = node.lineno - 1  # 0-indexed
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
        
        return '\n'.join(lines[start_line:end_line])
    
    def _parse_function(self, 
                       node: ast.FunctionDef, 
                       source: str, 
                       file_path: str,
                       imports: List[str]) -> Optional[CodeFragment]:
        """Parse a function definition"""
        try:
            source_code = self._get_source_segment(source, node)
            docstring = ast.get_docstring(node)
            
            # Build function signature
            args = [arg.arg for arg in node.args.args]
            signature = f"{node.name}({', '.join(args)})"
            
            # Infer metadata from function name and docstring
            metadata = self._infer_metadata(node.name, docstring, file_path)
            
            return CodeFragment(
                type='function',
                name=node.name,
                source_code=source_code,
                docstring=docstring,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                signature=signature,
                dependencies=imports,
                metadata=metadata,
                hash=""
            )
        except Exception as e:
            logger.warning(f"Failed to parse function {node.name}: {e}")
            return None
    
    def _parse_class(self,
                    node: ast.ClassDef,
                    source: str,
                    file_path: str,
                    imports: List[str]) -> Optional[CodeFragment]:
        """Parse a class definition"""
        try:
            source_code = self._get_source_segment(source, node)
            docstring = ast.get_docstring(node)
            
            # Get base classes
            bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
            signature = f"class {node.name}({', '.join(bases)})" if bases else f"class {node.name}"
            
            metadata = self._infer_metadata(node.name, docstring, file_path)
            metadata['bases'] = bases
            
            return CodeFragment(
                type='class',
                name=node.name,
                source_code=source_code,
                docstring=docstring,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                signature=signature,
                dependencies=imports,
                metadata=metadata,
                hash=""
            )
        except Exception as e:
            logger.warning(f"Failed to parse class {node.name}: {e}")
            return None
    
    def _parse_method(self,
                     node: ast.FunctionDef,
                     class_name: str,
                     source: str,
                     file_path: str,
                     imports: List[str]) -> Optional[CodeFragment]:
        """Parse a class method"""
        try:
            source_code = self._get_source_segment(source, node)
            docstring = ast.get_docstring(node)
            
            args = [arg.arg for arg in node.args.args if arg.arg != 'self']
            signature = f"{class_name}.{node.name}({', '.join(args)})"
            
            metadata = self._infer_metadata(node.name, docstring, file_path)
            metadata['class'] = class_name
            
            return CodeFragment(
                type='method',
                name=f"{class_name}.{node.name}",
                source_code=source_code,
                docstring=docstring,
                file_path=file_path,
                line_start=node.lineno,
                line_end=node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                signature=signature,
                dependencies=imports,
                metadata=metadata,
                hash=""
            )
        except Exception as e:
            logger.warning(f"Failed to parse method {node.name}: {e}")
            return None
    
    def _infer_metadata(self, name: str, docstring: Optional[str], file_path: str) -> Dict[str, Any]:
        """
        Infer metadata from name, docstring and file path
        Detects platform (instagram, tiktok) and action (login, like, follow)
        """
        metadata = {}
        
        # Platform detection
        name_lower = name.lower()
        path_lower = file_path.lower()
        
        if 'instagram' in path_lower or 'ig_' in name_lower or 'insta' in name_lower:
            metadata['platform'] = 'instagram'
        elif 'tiktok' in path_lower or 'tt_' in name_lower:
            metadata['platform'] = 'tiktok'
        elif 'twitter' in path_lower or 'tw_' in name_lower:
            metadata['platform'] = 'twitter'
        elif 'facebook' in path_lower or 'fb_' in name_lower:
            metadata['platform'] = 'facebook'
        else:
            metadata['platform'] = 'unknown'
        
        # Action detection
        actions = {
            'login': ['login', 'signin', 'authenticate'],
            'like': ['like', 'heart', 'favorite'],
            'follow': ['follow', 'subscribe'],
            'comment': ['comment', 'reply'],
            'post': ['post', 'upload', 'publish'],
            'scrape': ['scrape', 'extract', 'fetch', 'get'],
            'interact': ['interact', 'engage', 'click'],
            'navigate': ['navigate', 'goto', 'open']
        }
        
        for action, keywords in actions.items():
            if any(keyword in name_lower for keyword in keywords):
                metadata['action'] = action
                break
        else:
            metadata['action'] = 'unknown'
        
        # Extract from docstring if available
        if docstring:
            docstring_lower = docstring.lower()
            for action, keywords in actions.items():
                if any(keyword in docstring_lower for keyword in keywords):
                    metadata['action'] = action
                    break
        
        return metadata


class CodeIngestor:
    """Main ingestion pipeline: scan → parse → store"""
    
    def __init__(self, legacy_code_path: str = "./legacy_code"):
        self.legacy_code_path = Path(legacy_code_path)
        self.parser = ASTCodeParser()
        self.fragments: List[CodeFragment] = []
    
    def scan_and_parse(self) -> List[CodeFragment]:
        """
        Scan the legacy_code directory and parse all Python files
        
        Returns:
            List of all parsed CodeFragment objects
        """
        if not self.legacy_code_path.exists():
            logger.error(f"❌ Legacy code path does not exist: {self.legacy_code_path}")
            raise FileNotFoundError(f"Path not found: {self.legacy_code_path}")
        
        logger.info(f"🔍 Scanning {self.legacy_code_path} for Python files...")
        
        python_files = list(self.legacy_code_path.rglob("*.py"))
        logger.info(f"📂 Found {len(python_files)} Python files")
        
        all_fragments = []
        
        for py_file in python_files:
            logger.info(f"📖 Parsing {py_file}...")
            fragments = self.parser.parse_file(str(py_file))
            all_fragments.extend(fragments)
        
        self.fragments = all_fragments
        logger.info(f"✅ Total fragments extracted: {len(all_fragments)}")
        
        # Statistics
        stats = self._generate_stats()
        logger.info(f"📊 Statistics:\n{json.dumps(stats, indent=2)}")
        
        return all_fragments
    
    def _generate_stats(self) -> Dict[str, Any]:
        """Generate ingestion statistics"""
        if not self.fragments:
            return {}
        
        stats = {
            "total_fragments": len(self.fragments),
            "by_type": {},
            "by_platform": {},
            "by_action": {}
        }
        
        for fragment in self.fragments:
            # Type stats
            stats["by_type"][fragment.type] = stats["by_type"].get(fragment.type, 0) + 1
            
            # Platform stats
            platform = fragment.metadata.get('platform', 'unknown')
            stats["by_platform"][platform] = stats["by_platform"].get(platform, 0) + 1
            
            # Action stats
            action = fragment.metadata.get('action', 'unknown')
            stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
        
        return stats
    
    def export_to_json(self, output_path: str = "./data/code_fragments.json") -> None:
        """Export parsed fragments to JSON for inspection"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        fragments_dict = [asdict(f) for f in self.fragments]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(fragments_dict, f, indent=2)
        
        logger.info(f"💾 Exported {len(self.fragments)} fragments to {output_path}")


# CLI Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    import sys
    
    legacy_path = sys.argv[1] if len(sys.argv) > 1 else "./legacy_code"
    
    logger.info(f"🚀 Starting code ingestion from: {legacy_path}")
    
    ingestor = CodeIngestor(legacy_path)
    fragments = ingestor.scan_and_parse()
    
    # Export to JSON for inspection
    ingestor.export_to_json()
    
    print(f"\n✅ Ingestion complete!")
    print(f"📦 {len(fragments)} code fragments ready for vectorization")
    print(f"💾 Fragments exported to: ./data/code_fragments.json")
    
    # Show sample
    if fragments:
        print(f"\n📋 Sample fragment:")
        sample = fragments[0]
        print(f"  Type: {sample.type}")
        print(f"  Name: {sample.name}")
        print(f"  Platform: {sample.metadata.get('platform')}")
        print(f"  Action: {sample.metadata.get('action')}")
        print(f"  Lines: {sample.line_start}-{sample.line_end}")
