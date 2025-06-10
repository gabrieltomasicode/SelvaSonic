import os
import shutil

def remove_pycache_and_pyc(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove __pycache__ folders
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            print(f"Removendo: {pycache_path}")
            try:
                shutil.rmtree(pycache_path)
            except Exception as e:
                print(f"Erro ao remover {pycache_path}: {e}")
            dirnames.remove("__pycache__")
        # Remove .pyc files
        for filename in filenames:
            if filename.endswith(".pyc"):
                pyc_path = os.path.join(dirpath, filename)
                print(f"Removendo: {pyc_path}")
                os.remove(pyc_path)

if __name__ == "__main__":
    remove_pycache_and_pyc(os.getcwd())
    print("Limpeza de cache concluída!")