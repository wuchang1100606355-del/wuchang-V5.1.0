#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cloud_deployment.py

雲端部署自動化腳本

功能：
- 部署到 Google Cloud Run
- 部署到 Google Cloud SQL
- 部署到其他雲端平台
- 自動化配置和部署流程
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "my-j-483304")
REGION = os.getenv("GCP_REGION", "asia-east1")

def log(message: str, level: str = "INFO"):
    """記錄日誌"""
    icons = {
        "INFO": "ℹ️",
        "OK": "✅",
        "WARN": "⚠️",
        "ERROR": "❌",
        "PROGRESS": "🔄"
    }
    icon = icons.get(level, "•")
    print(f"{icon} [{level}] {message}")


def check_gcloud():
    """檢查 gcloud CLI 是否安裝"""
    try:
        result = subprocess.run(
            ["gcloud", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        log("✓ gcloud CLI 已安裝", "OK")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("❌ gcloud CLI 未安裝或未在 PATH 中", "ERROR")
        log("請安裝 Google Cloud SDK: https://cloud.google.com/sdk/docs/install", "INFO")
        return False


def check_docker():
    """檢查 Docker 是否安裝"""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        log("✓ Docker 已安裝", "OK")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log("❌ Docker 未安裝或未在 PATH 中", "ERROR")
        return False


def build_and_push_image(service_name: str, dockerfile_path: str):
    """建立並推送 Docker 映像檔到 Google Container Registry"""
    image_name = f"gcr.io/{PROJECT_ID}/{service_name}"
    
    log(f"正在建立映像檔: {image_name}", "PROGRESS")
    
    try:
        # 建立映像檔
        subprocess.run(
            ["docker", "build", "-t", image_name, "-f", dockerfile_path, "."],
            check=True
        )
        log(f"✓ 映像檔建立成功", "OK")
        
        # 推送到 GCR
        log("正在推送到 Google Container Registry...", "PROGRESS")
        subprocess.run(
            ["docker", "push", image_name],
            check=True
        )
        log(f"✓ 映像檔推送成功", "OK")
        
        return image_name
    except subprocess.CalledProcessError as e:
        log(f"❌ 建立或推送映像檔失敗: {e}", "ERROR")
        return None


def deploy_to_cloud_run(service_name: str, image_name: str):
    """部署到 Google Cloud Run"""
    log(f"正在部署到 Cloud Run: {service_name}", "PROGRESS")
    
    try:
        subprocess.run([
            "gcloud", "run", "deploy", service_name,
            "--image", image_name,
            "--platform", "managed",
            "--region", REGION,
            "--allow-unauthenticated",
            "--memory", "2Gi",
            "--cpu", "2",
            "--max-instances", "10",
            "--project", PROJECT_ID
        ], check=True)
        
        log(f"✓ 部署成功: {service_name}", "OK")
        return True
    except subprocess.CalledProcessError as e:
        log(f"❌ 部署失敗: {e}", "ERROR")
        return False


def create_cloud_sql_instance():
    """建立 Cloud SQL 資料庫實例"""
    instance_name = "wuchang-db-instance"
    
    log(f"正在建立 Cloud SQL 實例: {instance_name}", "PROGRESS")
    
    try:
        subprocess.run([
            "gcloud", "sql", "instances", "create", instance_name,
            "--database-version", "POSTGRES_15",
            "--tier", "db-f1-micro",
            "--region", REGION,
            "--project", PROJECT_ID
        ], check=True)
        
        log(f"✓ Cloud SQL 實例建立成功", "OK")
        return instance_name
    except subprocess.CalledProcessError as e:
        log(f"❌ 建立 Cloud SQL 實例失敗: {e}", "ERROR")
        return None


def main():
    """主程式"""
    print("=" * 70)
    print("雲端部署自動化工具")
    print("=" * 70)
    print()
    
    # 檢查必要工具
    if not check_gcloud():
        return 1
    
    if not check_docker():
        return 1
    
    # 檢查環境變數
    if not PROJECT_ID:
        log("❌ GCP_PROJECT_ID 未設定", "ERROR")
        log("請設定環境變數: export GCP_PROJECT_ID=your-project-id", "INFO")
        return 1
    
    log(f"使用 GCP 專案: {PROJECT_ID}", "INFO")
    log(f"使用區域: {REGION}", "INFO")
    print()
    
    # 部署選項
    print("請選擇部署方式：")
    print("  1. 部署到 Cloud Run (容器服務)")
    print("  2. 建立 Cloud SQL 資料庫")
    print("  3. 完整部署（Cloud Run + Cloud SQL）")
    print()
    
    choice = input("請選擇 (1-3): ").strip()
    
    if choice == "1":
        # 部署到 Cloud Run
        service_name = input("服務名稱 (預設: wuchang-web): ").strip() or "wuchang-web"
        dockerfile_path = input("Dockerfile 路徑 (預設: Dockerfile): ").strip() or "Dockerfile"
        
        image_name = build_and_push_image(service_name, dockerfile_path)
        if image_name:
            deploy_to_cloud_run(service_name, image_name)
    
    elif choice == "2":
        # 建立 Cloud SQL
        create_cloud_sql_instance()
    
    elif choice == "3":
        # 完整部署
        instance_name = create_cloud_sql_instance()
        if instance_name:
            service_name = "wuchang-web"
            dockerfile_path = "Dockerfile"
            image_name = build_and_push_image(service_name, dockerfile_path)
            if image_name:
                deploy_to_cloud_run(service_name, image_name)
    
    else:
        log("無效的選擇", "ERROR")
        return 1
    
    log("✅ 部署流程完成！", "OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
