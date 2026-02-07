"""檢查由用戶運行的容器"""
import subprocess
import sys

# 設定 UTF-8 編碼
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

def get_containers_info():
    """取得容器資訊"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode != 0:
            return []
        
        containers = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        # 檢查每個容器是否由 docker-compose 管理
        my_containers = []
        other_containers = []
        
        for container in containers:
            # 檢查是否有 docker-compose 標籤
            inspect_result = subprocess.run(
                ["docker", "inspect", container, "--format", "{{index .Config.Labels \"com.docker.compose.project\"}}"],
                capture_output=True,
                text=True,
                timeout=5,
                encoding='utf-8',
                errors='replace'
            )
            
            if inspect_result.returncode == 0 and inspect_result.stdout.strip():
                project = inspect_result.stdout.strip()
                # 檢查工作目錄
                workdir_result = subprocess.run(
                    ["docker", "inspect", container, "--format", "{{index .Config.Labels \"com.docker.compose.project.working_dir\"}}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding='utf-8',
                    errors='replace'
                )
                workdir = workdir_result.stdout.strip() if workdir_result.returncode == 0 else ""
                
                # 檢查是否在當前工作目錄
                if "wuchang V5.1.0" in workdir or project == "wuchangv510":
                    my_containers.append((container, project, workdir))
                else:
                    other_containers.append((container, project, workdir))
            else:
                other_containers.append((container, "無標籤", ""))
        
        return my_containers, other_containers
    except Exception as e:
        print(f"錯誤: {e}")
        return [], []

def main():
    print("=" * 70)
    print("檢查由您運行的容器")
    print("=" * 70)
    print()
    
    my_containers, other_containers = get_containers_info()
    
    print("【由您運行的容器（docker-compose 管理）】")
    print()
    
    if my_containers:
        for i, (container, project, workdir) in enumerate(my_containers, 1):
            print(f"{i}. {container}")
            print(f"   專案: {project}")
            if workdir:
                print(f"   工作目錄: {workdir}")
            print()
        
        print("=" * 70)
        print(f"總計：{len(my_containers)} 個容器由您運行")
        print("=" * 70)
    else:
        print("未找到由您運行的容器")
        print()
    
    if other_containers:
        print()
        print("【其他容器】")
        print()
        for container, project, workdir in other_containers:
            print(f"  - {container} (專案: {project})")
        print()

if __name__ == "__main__":
    main()
