#!/usr/bin/env python3
"""
KRP 패키지 관리자
KRP 언어용 패키지를 설치하고 관리합니다.
"""

import os
import sys
import json
import shutil
import argparse
from pathlib import Path

class KRPPackageManager:
    def __init__(self):
        self.home_dir = Path.home() / '.krp'
        self.packages_dir = self.home_dir / 'packages'
        self.installed_file = self.home_dir / 'installed.json'
        
        # 디렉토리 생성
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        
        # 설치된 패키지 목록 로드
        self.installed = self._load_installed()
    
    def _load_installed(self):
        """설치된 패키지 목록 로드"""
        if self.installed_file.exists():
            with open(self.installed_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_installed(self):
        """설치된 패키지 목록 저장"""
        with open(self.installed_file, 'w', encoding='utf-8') as f:
            json.dump(self.installed, f, ensure_ascii=False, indent=2)
    
    def install(self, package_name, source=None):
        """패키지 설치"""
        print(f"📦 '{package_name}' 패키지 설치 중...")
        
        if source:
            # 로컬 경로에서 설치
            source_path = Path(source)
            if not source_path.exists():
                print(f"❌ 오류: 경로를 찾을 수 없습니다: {source}")
                return False
            
            dest_path = self.packages_dir / package_name
            if dest_path.exists():
                shutil.rmtree(dest_path)
            
            shutil.copytree(source_path, dest_path)
            
            self.installed[package_name] = {
                'version': '1.0.0',
                'source': str(source_path),
                'type': 'local'
            }
            self._save_installed()
            print(f"✅ '{package_name}' 패키지가 설치되었습니다.")
            return True
        else:
            print("❌ 오류: 원격 저장소 기능은 아직 구현되지 않았습니다.")
            print("   로컬 패키지를 설치하려면: krp-pkg install <패키지명> --source <경로>")
            return False
    
    def uninstall(self, package_name):
        """패키지 제거"""
        if package_name not in self.installed:
            print(f"❌ 오류: '{package_name}' 패키지가 설치되어 있지 않습니다.")
            return False
        
        print(f"🗑️  '{package_name}' 패키지 제거 중...")
        
        package_path = self.packages_dir / package_name
        if package_path.exists():
            shutil.rmtree(package_path)
        
        del self.installed[package_name]
        self._save_installed()
        
        print(f"✅ '{package_name}' 패키지가 제거되었습니다.")
        return True
    
    def list_packages(self):
        """설치된 패키지 목록 표시"""
        if not self.installed:
            print("📦 설치된 패키지가 없습니다.")
            return
        
        print("📦 설치된 패키지 목록:")
        print("-" * 60)
        for name, info in self.installed.items():
            version = info.get('version', '알 수 없음')
            pkg_type = info.get('type', '알 수 없음')
            print(f"  • {name} (v{version}) - {pkg_type}")
        print("-" * 60)
        print(f"총 {len(self.installed)}개의 패키지가 설치되어 있습니다.")
    
    def info(self, package_name):
        """패키지 정보 표시"""
        if package_name not in self.installed:
            print(f"❌ 오류: '{package_name}' 패키지가 설치되어 있지 않습니다.")
            return False
        
        info = self.installed[package_name]
        print(f"📦 패키지 정보: {package_name}")
        print("-" * 60)
        print(f"  버전: {info.get('version', '알 수 없음')}")
        print(f"  타입: {info.get('type', '알 수 없음')}")
        print(f"  소스: {info.get('source', '알 수 없음')}")
        print("-" * 60)
        return True
    
    def create_package(self, package_name, path='.'):
        """새 패키지 템플릿 생성"""
        package_path = Path(path) / package_name
        
        if package_path.exists():
            print(f"❌ 오류: '{package_path}' 디렉토리가 이미 존재합니다.")
            return False
        
        print(f"📦 '{package_name}' 패키지 생성 중...")
        
        # 디렉토리 구조 생성
        package_path.mkdir(parents=True)
        (package_path / 'src').mkdir()
        
        # package.json 생성
        package_json = {
            'name': package_name,
            'version': '1.0.0',
            'description': f'{package_name} 패키지',
            'main': 'src/main.한글',
            'author': '',
            'license': 'MIT'
        }
        
        with open(package_path / 'package.json', 'w', encoding='utf-8') as f:
            json.dump(package_json, f, ensure_ascii=False, indent=2)
        
        # README.md 생성
        readme = f"""# {package_name}

{package_name} 패키지입니다.

## 설치

```bash
krp-pkg install {package_name} --source ./{package_name}
```

## 사용법

```korean
가져오기 {package_name}
```

## 라이선스

MIT
"""
        with open(package_path / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme)
        
        # 메인 파일 생성
        main_code = f"""# {package_name} 메인 파일

함수 안녕():
    보여줘("안녕하세요! {package_name} 패키지입니다.")
    반환 참
"""
        with open(package_path / 'src' / 'main.한글', 'w', encoding='utf-8') as f:
            f.write(main_code)
        
        print(f"✅ '{package_name}' 패키지가 생성되었습니다: {package_path}")
        print(f"   다음 명령으로 설치할 수 있습니다:")
        print(f"   krp-pkg install {package_name} --source {package_path}")
        return True

def main():
    parser = argparse.ArgumentParser(
        description='KRP 패키지 관리자',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예제:
  krp-pkg list                              # 설치된 패키지 목록
  krp-pkg install mypackage --source ./pkg  # 로컬 패키지 설치
  krp-pkg uninstall mypackage               # 패키지 제거
  krp-pkg info mypackage                    # 패키지 정보
  krp-pkg create mypackage                  # 새 패키지 생성
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='명령')
    
    # install 명령
    install_parser = subparsers.add_parser('install', help='패키지 설치')
    install_parser.add_argument('package', help='패키지 이름')
    install_parser.add_argument('--source', help='로컬 패키지 경로')
    
    # uninstall 명령
    uninstall_parser = subparsers.add_parser('uninstall', help='패키지 제거')
    uninstall_parser.add_argument('package', help='패키지 이름')
    
    # list 명령
    list_parser = subparsers.add_parser('list', help='설치된 패키지 목록')
    
    # info 명령
    info_parser = subparsers.add_parser('info', help='패키지 정보')
    info_parser.add_argument('package', help='패키지 이름')
    
    # create 명령
    create_parser = subparsers.add_parser('create', help='새 패키지 생성')
    create_parser.add_argument('package', help='패키지 이름')
    create_parser.add_argument('--path', default='.', help='생성 경로 (기본: 현재 디렉토리)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = KRPPackageManager()
    
    if args.command == 'install':
        manager.install(args.package, args.source)
    elif args.command == 'uninstall':
        manager.uninstall(args.package)
    elif args.command == 'list':
        manager.list_packages()
    elif args.command == 'info':
        manager.info(args.package)
    elif args.command == 'create':
        manager.create_package(args.package, args.path)

if __name__ == '__main__':
    main()
