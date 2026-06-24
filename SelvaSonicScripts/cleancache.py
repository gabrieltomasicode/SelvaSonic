import os
import shutil
import stat

def handle_remove_readonly(func, path, exc_info):
    """
    Remove o atributo 'somente leitura' de arquivos bloqueados (comum no OneDrive)
    e tenta realizar a exclusão novamente.
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        # Se o arquivo estiver sendo usado ativamente pelo interpretador, ignoramos.
        pass

def remove_pycache_and_pyc(root_dir=None):
    """
    Remove todas as pastas __pycache__ e arquivos .pyc recursivamente.
    Se root_dir não for fornecido, usa o diretório onde este script está localizado.
    """
    if root_dir is None:
        root_dir = os.path.dirname(os.path.abspath(__file__))

    for dirpath, dirnames, filenames in os.walk(root_dir):
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            print(f"Limpando cache em: {pycache_path}")
            try:
                shutil.rmtree(pycache_path, onerror=handle_remove_readonly)
            except Exception:
                pass
            dirnames.remove("__pycache__")
        
        # Varredura extra para arquivos .pyc soltos
        for filename in filenames:
            if filename.endswith(".pyc"):
                pyc_path = os.path.join(dirpath, filename)
                try:
                    os.chmod(pyc_path, stat.S_IWRITE)
                    os.remove(pyc_path)
                except Exception:
                    pass

if __name__ == "__main__":
    print("Iniciando limpeza manual de cache...")
    remove_pycache_and_pyc()
    print("Limpeza de cache concluída!")