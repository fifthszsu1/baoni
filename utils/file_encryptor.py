#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件加密解密工具
支持对文件和文件夹进行AES加密，生成随机名称的.cab文件
"""

import os
import sys
import json
import random
import string
import zipfile
import argparse
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class FileEncryptor:
    def __init__(self):
        self.key_length = 32  # AES-256
        self.iv_length = 16   # AES block size
        self.salt_length = 16
        
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """从密码和盐值派生加密密钥"""
        return PBKDF2(password, salt, self.key_length, count=100000)
    
    def _generate_random_filename(self, length: int = 10) -> str:
        """生成随机文件名"""
        chars = string.ascii_letters + string.digits + '_'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def _compress_path(self, source_path: str, temp_zip_path: str):
        """将文件或文件夹压缩为zip文件"""
        source_path = Path(source_path)
        
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if source_path.is_file():
                # 如果是文件，直接添加
                zipf.write(source_path, source_path.name)
            elif source_path.is_dir():
                # 如果是文件夹，递归添加所有文件
                for file_path in source_path.rglob('*'):
                    if file_path.is_file():
                        # 计算相对路径
                        arcname = file_path.relative_to(source_path.parent)
                        zipf.write(file_path, arcname)
    
    def encrypt_file(self, source_path: str, password: str, output_dir: str = None) -> str:
        """
        加密文件或文件夹
        
        Args:
            source_path: 要加密的文件或文件夹路径
            password: 加密密码
            output_dir: 输出目录，默认为当前目录
            
        Returns:
            加密后的文件路径
        """
        source_path = Path(source_path)
        if not source_path.exists():
            raise FileNotFoundError(f"源文件或文件夹不存在: {source_path}")
        
        # 设置输出目录
        if output_dir is None:
            output_dir = source_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成随机输出文件名
        random_name = self._generate_random_filename()
        output_file = output_dir / f"{random_name}.cab"
        
        # 创建临时zip文件
        temp_zip = output_dir / f"temp_{random_name}.zip"
        
        try:
            print(f"正在压缩 {source_path}...")
            self._compress_path(source_path, temp_zip)
            
            # 读取压缩文件
            with open(temp_zip, 'rb') as f:
                data = f.read()
            
            # 生成加密参数
            salt = get_random_bytes(self.salt_length)
            iv = get_random_bytes(self.iv_length)
            key = self._derive_key(password, salt)
            
            # 加密数据
            print("正在加密...")
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = pad(data, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # 创建元数据
            metadata = {
                'original_name': source_path.name,
                'is_directory': source_path.is_dir(),
                'salt': salt.hex(),
                'iv': iv.hex()
            }
            metadata_json = json.dumps(metadata).encode('utf-8')
            metadata_length = len(metadata_json)
            
            # 写入加密文件
            with open(output_file, 'wb') as f:
                # 写入元数据长度（4字节）
                f.write(metadata_length.to_bytes(4, byteorder='big'))
                # 写入元数据
                f.write(metadata_json)
                # 写入加密数据
                f.write(encrypted_data)
            
            print(f"加密完成: {output_file}")
            return str(output_file)
            
        finally:
            # 清理临时文件
            if temp_zip.exists():
                temp_zip.unlink()
    
    def decrypt_file(self, encrypted_file: str, password: str, output_dir: str = None) -> str:
        """
        解密文件
        
        Args:
            encrypted_file: 加密文件路径
            password: 解密密码
            output_dir: 输出目录，默认为当前目录
            
        Returns:
            解密后的文件或文件夹路径
        """
        encrypted_file = Path(encrypted_file)
        if not encrypted_file.exists():
            raise FileNotFoundError(f"加密文件不存在: {encrypted_file}")
        
        # 设置输出目录
        if output_dir is None:
            output_dir = encrypted_file.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(encrypted_file, 'rb') as f:
            # 读取元数据长度
            metadata_length = int.from_bytes(f.read(4), byteorder='big')
            
            # 读取元数据
            metadata_json = f.read(metadata_length)
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            # 读取加密数据
            encrypted_data = f.read()
        
        # 提取加密参数
        salt = bytes.fromhex(metadata['salt'])
        iv = bytes.fromhex(metadata['iv'])
        key = self._derive_key(password, salt)
        
        # 解密数据
        print("正在解密...")
        try:
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = cipher.decrypt(encrypted_data)
            data = unpad(padded_data, AES.block_size)
        except ValueError as e:
            raise ValueError("解密失败，可能是密码错误") from e
        
        # 创建临时zip文件
        temp_zip = output_dir / f"temp_decrypt_{random.randint(1000, 9999)}.zip"
        
        try:
            # 写入解密数据到临时zip文件
            with open(temp_zip, 'wb') as f:
                f.write(data)
            
            # 确定输出路径
            original_name = metadata['original_name']
            is_directory = metadata['is_directory']
            output_path = output_dir / original_name
            
            # 如果输出路径已存在，添加数字后缀
            counter = 1
            base_output_path = output_path
            while output_path.exists():
                if is_directory:
                    output_path = base_output_path.parent / f"{base_output_path.name}_{counter}"
                else:
                    stem = base_output_path.stem
                    suffix = base_output_path.suffix
                    output_path = base_output_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1
            
            # 解压文件
            print(f"正在解压到 {output_path}...")
            with zipfile.ZipFile(temp_zip, 'r') as zipf:
                if is_directory:
                    # 如果原来是文件夹，解压到指定目录
                    zipf.extractall(output_dir)
                    # 重命名解压出的文件夹
                    extracted_items = list(output_dir.glob(f"{original_name}*"))
                    if extracted_items:
                        extracted_path = extracted_items[0]
                        if extracted_path != output_path:
                            extracted_path.rename(output_path)
                else:
                    # 如果原来是文件，解压并重命名
                    zipf.extractall(output_dir)
                    # 找到解压出的文件并重命名
                    for item in zipf.namelist():
                        extracted_file = output_dir / item
                        if extracted_file.exists() and extracted_file != output_path:
                            extracted_file.rename(output_path)
                            break
            
            print(f"解密完成: {output_path}")
            return str(output_path)
            
        finally:
            # 清理临时文件
            if temp_zip.exists():
                temp_zip.unlink()


def main():
    parser = argparse.ArgumentParser(description='文件加密解密工具')
    parser.add_argument('action', choices=['encrypt', 'decrypt'], help='操作类型：encrypt（加密）或 decrypt（解密）')
    parser.add_argument('file_path', help='文件或文件夹路径')
    parser.add_argument('password', help='加密/解密密码')
    parser.add_argument('-o', '--output', help='输出目录（可选）')
    
    args = parser.parse_args()
    
    encryptor = FileEncryptor()
    
    try:
        if args.action == 'encrypt':
            result = encryptor.encrypt_file(args.file_path, args.password, args.output)
            print(f"\n✅ 加密成功！")
            print(f"输出文件: {result}")
        else:  # decrypt
            result = encryptor.decrypt_file(args.file_path, args.password, args.output)
            print(f"\n✅ 解密成功！")
            print(f"输出路径: {result}")
            
    except Exception as e:
        print(f"\n❌ 操作失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
