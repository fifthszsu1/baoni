#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查服务
基于comprehensive_health_checker.py的功能，提供API接口
"""

import json
import requests
import time
import logging
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class HealthCheckService:
    """健康检查服务类"""
    
    def __init__(self, timeout=30):
        """初始化健康检查服务"""
        self.timeout = timeout
        
        # 定义要检查的端点（基于原始comprehensive_health_checker.py）
        self.endpoints = [
            # ========== oat.sc.com (认证服务) ==========
            {
                'name': 'OAT - 获取服务器详情',
                'domain': 'oat.sc.com',
                'url': 'https://oat.sc.com/retail/api/v3/security/server-details',
                'method': 'GET',
                'headers': {
                    'Accept': '*/*',
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 16)',
                },
                'payload': None,
                'expected_status': [200, 401, 403, 500]
            },
            {
                'name': 'OAT - 开户初始化',
                'domain': 'oat.sc.com',
                'url': 'https://oat.sc.com/retail/api/v3/auth/sign-up/init',
                'method': 'POST',
                'headers': {
                    'country': 'HK',
                    'Authorization': 'Bearer dummy',
                    'Content-Type': 'application/json; charset=utf-8',
                },
                'payload': {
                    'sign-up-attributes': {
                        'mobile': '+8612345678901',
                        'emailId': 'healthcheck@example.com',
                        'country': 'HK',
                        'payloadVerifier': 'dummy_health_check',
                        'app-origin': 'PersonalBanking'
                    }
                },
                'expected_status': [200, 400, 401, 500]
            },
            
            # ========== staging-ob.sc.com (业务服务) ==========
            {
                'name': 'Staging-OB - 首页',
                'domain': 'staging-ob.sc.com',
                'url': 'https://staging-ob.sc.com/hk/ib/casa/index.html',
                'method': 'GET',
                'headers': {
                    'Accept': 'text/html',
                },
                'payload': None,
                'expected_status': [200, 301, 302, 403, 404]
            },
            {
                'name': 'Staging-OB - GraphQL接口',
                'domain': 'staging-ob.sc.com',
                'url': 'https://staging-ob.sc.com/hk/api/v4/ib/casa/',
                'method': 'POST',
                'headers': {
                    'Authorization': 'Bearer dummy',
                    'Content-Type': 'application/json',
                },
                'payload': {
                    'query': 'mutation { test }',
                    'variables': {'payloadVerifier': 'dummy_health_check'}
                },
                'expected_status': [200, 400, 401, 500]
            },
            {
                'name': 'Staging-OB - 查询申请',
                'domain': 'staging-ob.sc.com',
                'url': 'https://staging-ob.sc.com/hk/api/v4/ib/casa/application/enquiry',
                'method': 'POST',
                'headers': {
                    'Authorization': 'Bearer dummy',
                    'Content-Type': 'application/json',
                },
                'payload': {
                    'emailId': 'healthcheck@example.com',
                    'journey': 'GC',
                    'payloadVerifier': 'dummy_health_check'
                },
                'expected_status': [200, 400, 401, 500]
            },
            {
                'name': 'Staging-OB - 获取参考数据',
                'domain': 'staging-ob.sc.com',
                'url': 'https://staging-ob.sc.com/hk/api/v4/ib/casa/application/reference',
                'method': 'POST',
                'headers': {
                    'Authorization': 'Bearer dummy',
                    'Content-Type': 'application/json',
                },
                'payload': {
                    'country': 'HK',
                    'logicalField': 'test',
                    'payloadVerifier': 'dummy_health_check'
                },
                'expected_status': [200, 400, 401, 500]
            },
            {
                'name': 'Staging-OB - 中文转拼音',
                'domain': 'staging-ob.sc.com',
                'url': 'https://staging-ob.sc.com/hk/api/v4/ib/casa/application/pinyin',
                'method': 'POST',
                'headers': {
                    'Authorization': 'Bearer dummy',
                    'Content-Type': 'application/json',
                },
                'payload': {
                    'chineseName': '测试',
                    'payloadVerifier': 'dummy_health_check'
                },
                'expected_status': [200, 400, 401, 500]
            },
        ]
    
    def check_endpoint(self, endpoint: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """检查单个端点"""
        result = {
            'name': endpoint['name'],
            'domain': endpoint['domain'],
            'url': endpoint['url'],
            'status': 'unknown',
            'status_code': None,
            'response_time': None,
            'error': None,
            'healthy': False
        }
        
        start_time = time.time()
        
        try:
            kwargs = {
                'method': endpoint['method'],
                'url': endpoint['url'],
                'headers': endpoint['headers'],
                'timeout': timeout
            }
            
            if endpoint['payload']:
                kwargs['json'] = endpoint['payload']
            
            resp = requests.request(**kwargs)
            
            result['response_time'] = round((time.time() - start_time) * 1000, 2)
            result['status_code'] = resp.status_code
            
            # 判断是否健康
            if resp.status_code in endpoint['expected_status']:
                result['status'] = 'healthy'
                result['healthy'] = True
            else:
                result['status'] = 'unexpected_status'
                result['healthy'] = False
            
        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['error'] = 'Request timeout'
            result['healthy'] = False
            result['response_time'] = timeout * 1000
            
        except requests.exceptions.ConnectionError:
            result['status'] = 'connection_error'
            result['error'] = 'Cannot connect to server'
            result['healthy'] = False
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['healthy'] = False
        
        return result
    
    def perform_health_check(self) -> Dict[str, Any]:
        """执行完整的健康检查"""
        logger.info("开始执行健康检查...")
        
        start_time = time.time()
        results = []
        
        # 检查所有端点
        for i, endpoint in enumerate(self.endpoints, 1):
            logger.info(f"检查端点 [{i}/{len(self.endpoints)}]: {endpoint['name']}")
            result = self.check_endpoint(endpoint, timeout=10)
            results.append(result)
            
            # 避免请求过快
            time.sleep(0.3)
        
        # 计算总体统计
        total_check_time = round((time.time() - start_time) * 1000, 2)
        
        # 按域名分组统计
        domain_stats = defaultdict(lambda: {'total': 0, 'healthy': 0, 'results': []})
        
        for result in results:
            domain = result['domain']
            domain_stats[domain]['total'] += 1
            if result['healthy']:
                domain_stats[domain]['healthy'] += 1
            domain_stats[domain]['results'].append(result)
        
        # 计算域名健康状况
        domain_summary = {}
        for domain, stats in domain_stats.items():
            health_ratio = stats['healthy'] / stats['total']
            
            if health_ratio == 1.0:
                status = 'all_healthy'
                status_text = '全部正常'
            elif health_ratio > 0:
                status = 'partially_healthy'
                status_text = '部分异常'
            else:
                status = 'all_unhealthy'
                status_text = '全部异常'
            
            domain_summary[domain] = {
                'status': status,
                'status_text': status_text,
                'healthy_count': stats['healthy'],
                'total_count': stats['total'],
                'health_ratio': round(health_ratio, 2),
                'endpoints': stats['results']
            }
        
        # 总体统计
        total_endpoints = len(results)
        healthy_endpoints = sum(1 for r in results if r['healthy'])
        total_domains = len(domain_stats)
        healthy_domains = sum(1 for d in domain_stats.values() if d['healthy'] == d['total'])
        
        overall_ratio = healthy_endpoints / total_endpoints if total_endpoints > 0 else 0
        
        # 确定总体状态
        if overall_ratio == 1.0:
            overall_status = 'all_healthy'
            overall_message = '所有服务正常运行'
        elif overall_ratio >= 0.7:
            overall_status = 'mostly_healthy'
            overall_message = '大部分服务正常，少数存在问题'
        elif overall_ratio >= 0.3:
            overall_status = 'partially_healthy'
            overall_message = '部分服务存在问题'
        else:
            overall_status = 'mostly_unhealthy'
            overall_message = '多数服务不可用'
        
        # 构建响应数据
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'check_duration_ms': total_check_time,
            'overall_status': overall_status,
            'overall_message': overall_message,
            'summary': {
                'total_domains': total_domains,
                'healthy_domains': healthy_domains,
                'total_endpoints': total_endpoints,
                'healthy_endpoints': healthy_endpoints,
                'overall_health_ratio': round(overall_ratio, 2)
            },
            'domains': domain_summary,
            'detailed_results': results
        }
        
        logger.info(f"健康检查完成，总体状态: {overall_status}, 耗时: {total_check_time}ms")
        
        return {
            'success': True,
            'health_report': health_report
        }
    
    def get_quick_status(self) -> Dict[str, Any]:
        """获取快速状态检查（仅检查关键端点）"""
        try:
            # 选择几个关键端点进行快速检查
            key_endpoints = [
                self.endpoints[0],  # OAT服务器详情
                self.endpoints[2],  # Staging-OB首页
            ]
            
            results = []
            for endpoint in key_endpoints:
                result = self.check_endpoint(endpoint, timeout=5)
                results.append(result)
            
            healthy_count = sum(1 for r in results if r['healthy'])
            total_count = len(results)
            health_ratio = healthy_count / total_count if total_count > 0 else 0
            
            if health_ratio == 1.0:
                status = 'healthy'
                message = '关键服务正常'
            elif health_ratio > 0:
                status = 'degraded'
                message = '部分关键服务异常'
            else:
                status = 'unhealthy'
                message = '关键服务不可用'
            
            return {
                'success': True,
                'status': status,
                'message': message,
                'healthy_count': healthy_count,
                'total_count': total_count,
                'health_ratio': round(health_ratio, 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"快速状态检查失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'status': 'error',
                'message': '健康检查服务异常'
            }
