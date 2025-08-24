import requests
import json
import time

def test_health_check():
    """测试健康检查接口"""
    print("=== 测试健康检查接口 ===")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_connection():
    """测试Azure OpenAI连接"""
    print("\n=== 测试Azure OpenAI连接 ===")
    try:
        response = requests.get("http://localhost:5000/api/analyze/test")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False

def test_text_analysis():
    """测试文本分析接口"""
    print("\n=== 测试文本分析接口 ===")
    
    # 测试文本
    test_text = """To the members of the city council of Albion,

As a lifelong person living in Albion I have seen many changes to our beautiful town. Fifty years ago, the population was 32,000 and Main Street was the center of everything. People went there to shop, eat in restaurants, see movies, and sometimes just walk around. Today, Albion's population is over 80,000 and nobody even thinks about going downtown. We shop at malls and on the Internet. We take our fast food and stay home and watch TV. Most of the downtown businesses have closed, putting people out of work.

I advocate a suggestion to turn things around. Let's declare the four block area to the north of Main Street a pedestrian-only zone. Once we do that, we can begin creating a lively street scene with open-air markets, sidewalk cafes, and street musicians or other performers. People may start making downtown their free-time destination. Parents can bring their children, and teenagers would be able to get together in a public setting.

The changes could also have economic benefits for the city. Art galleries, clothing stores, and other businesses might begin to change the abandoned stores into new businesses. As downtown street life becomes more exciting, Main Street could also begin to attract new people living there. Young people responding to the energizing atmosphere may move into the apartments above the stores. New apartments will be built, providing new housing as well as work for local people. All of the activity would help to bring back the city's commercial tax base.

If you want confirmation that this kind of plan works, just look at Springfield's results. When they instituted their pedestrian-only zone in 2009, the changes were great. Restaurants and hotels began to fill up and unemployment rates went down. The people of the town gained an exciting new neighborhood. I certainly hope you'll give this idea your serious consideration.

Yours truly,

Mary Blakely"""
    
    payload = {
        "text": test_text
    }
    
    try:
        print("发送分析请求...")
        response = requests.post(
            "http://localhost:5000/api/analyze/text",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 分析成功!")
            print(f"使用的Token数量: {result.get('tokens_used', 'N/A')}")
            print(f"XMind文件名: {result.get('xmind_filename', 'N/A')}")
            print(f"下载链接: {result.get('download_url', 'N/A')}")
            
            # 显示分析结果的前200个字符
            analysis = result.get('analysis', '')
            if analysis:
                print(f"\n分析结果预览 (前200字符):")
                print(analysis[:200] + "..." if len(analysis) > 200 else analysis)
            
            return True
        else:
            print(f"❌ 分析失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_swagger_docs():
    """测试Swagger文档访问"""
    print("\n=== 测试Swagger文档 ===")
    try:
        response = requests.get("http://localhost:5000/swagger/")
        print(f"Swagger文档状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ Swagger文档可访问")
            print("📖 访问地址: http://localhost:5000/swagger/")
            return True
        else:
            print("❌ Swagger文档不可访问")
            return False
    except Exception as e:
        print(f"❌ Swagger文档测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试英文文本分析与XMind生成服务")
    print("=" * 50)
    
    # 等待服务完全启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 执行测试
    tests = [
        ("健康检查", test_health_check),
        ("Azure OpenAI连接", test_connection),
        ("文本分析", test_text_analysis),
        ("Swagger文档", test_swagger_docs)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果摘要
    print("\n" + "=" * 50)
    print("📊 测试结果摘要:")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总计: {passed}/{len(results)} 个测试通过")
    
    if passed == len(results):
        print("🎉 所有测试通过！服务运行正常。")
    else:
        print("⚠️  部分测试失败，请检查服务配置。")

if __name__ == "__main__":
    main() 