#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查API测试脚本
"""

import requests
import json
import sys

def test_health_api(base_url='http://localhost:5001'):
    """测试健康检查API"""
    
    print("测试健康检查API...")
    print(f"基础URL: {base_url}")
    print("=" * 50)
    
    # 测试快速状态检查
    print("1. 测试快速状态检查 (/api/health/status)")
    try:
        response = requests.get(f"{base_url}/api/health/status", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功: {data.get('success')}")
            print(f"   状态: {data.get('status')}")
            print(f"   消息: {data.get('message')}")
            print(f"   健康比例: {data.get('health_ratio')}")
            print("   ✅ 快速状态检查正常")
        else:
            print(f"   ❌ 快速状态检查失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 快速状态检查异常: {str(e)}")
    
    print()
    
    # 测试完整健康检查
    print("2. 测试完整健康检查 (/api/health/check)")
    print("   注意: 这可能需要较长时间...")
    try:
        response = requests.get(f"{base_url}/api/health/check", timeout=60)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   成功: {data.get('success')}")
            
            if data.get('health_report'):
                report = data['health_report']
                print(f"   总体状态: {report.get('overall_status')}")
                print(f"   总体消息: {report.get('overall_message')}")
                print(f"   检查耗时: {report.get('check_duration_ms')}ms")
                
                summary = report.get('summary', {})
                print(f"   域名统计: {summary.get('healthy_domains')}/{summary.get('total_domains')} 健康")
                print(f"   端点统计: {summary.get('healthy_endpoints')}/{summary.get('total_endpoints')} 健康")
                print(f"   整体健康比例: {summary.get('overall_health_ratio')}")
                
            print("   ✅ 完整健康检查正常")
        else:
            print(f"   ❌ 完整健康检查失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 完整健康检查异常: {str(e)}")
    
    print()
    print("=" * 50)
    print("健康检查API测试完成")

if __name__ == '__main__':
    # 可以通过命令行参数指定基础URL
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5001'
    test_health_api(base_url)
