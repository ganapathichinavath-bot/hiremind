import shutil
from pathlib import Path

# Base workspace path
base_dir = Path(__file__).resolve().parent

# List of files and folders to delete
paths_to_delete = [
    # Next.js folders and configs in frontend/
    base_dir / "frontend" / "app",
    base_dir / "frontend" / "components" / "DashboardLayout.tsx",
    base_dir / "frontend" / "lib",
    base_dir / "frontend" / "next.config.mjs",
    base_dir / "frontend" / "postcss.config.mjs",
    base_dir / "frontend" / "tailwind.config.ts",
    base_dir / "frontend" / "next-env.d.ts",
    base_dir / "frontend" / "vercel.json",
    
    # Old Streamlit/Obsolete files in root
    base_dir / "app.py",
    base_dir / "Procfile",
    base_dir / ".streamlit",
    
    # Old files in backend/
    base_dir / "backend" / "main.py",
    base_dir / "backend" / "Procfile",
    base_dir / "backend" / "candidate_ranker.db",
]

for p in paths_to_delete:
    if p.exists():
        try:
            if p.is_dir():
                shutil.rmtree(p)
                print(f"Successfully deleted directory: {p.relative_to(base_dir)}")
            else:
                p.unlink()
                print(f"Successfully deleted file: {p.relative_to(base_dir)}")
        except Exception as e:
            print(f"Failed to delete {p.relative_to(base_dir)}: {e}")
    else:
        print(f"Path does not exist (already removed): {p.relative_to(base_dir) if p.parent.exists() else p.name}")
