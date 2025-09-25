import openai
from openai import AzureOpenAI
import logging
from typing import Optional, Dict, Any
from config import Config
import base64

logger = logging.getLogger(__name__)

class OpenAIService:
    """Azure OpenAI服务类"""
    
    def __init__(self):
        """初始化Azure OpenAI客户端"""
        self.client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT
        )
        self.deployment_name = Config.AZURE_DEPLOYMENT_NAME

    def extract_text_from_image(self, image_data: bytes) -> Optional[Dict[str, Any]]:
        """
        从图片中提取英文文章内容
        
        Args:
            image_data (bytes): 图片的二进制数据
            
        Returns:
            Dict: 包含提取结果的字典
        """
        try:
            # 将图片转换为base64编码
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # 构建专门用于OCR的提示词
            system_prompt = """You are a professional OCR (Optical Character Recognition) assistant. Your task is to extract all English text content from the uploaded image accurately.

IMPORTANT INSTRUCTIONS:
1. Extract ALL visible English text from the image, maintaining the original structure and formatting as much as possible
2. If the image contains an English article, essay, or document, transcribe it completely
3. Preserve paragraph breaks, bullet points, and basic formatting
4. If there are titles, headings, or subheadings, include them
5. Only extract text - do not add explanations, comments, or descriptions about the image
6. If the text is unclear or partially obscured, do your best to transcribe what is visible
7. If no English text is found, respond with "No English text detected in the image"

Please provide the extracted text directly without any additional commentary."""

            user_prompt = "Please extract all English text content from this image:"
            
            # 调用GPT-4 Vision API
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # 需要支持vision的模型
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,  # 低温度确保准确性
                max_tokens=2000
            )
            
            extracted_text = response.choices[0].message.content
            
            # 检查是否成功提取到文本
            if extracted_text and extracted_text.strip() != "No English text detected in the image":
                return {
                    'success': True,
                    'extracted_text': extracted_text.strip(),
                    'tokens_used': response.usage.total_tokens if response.usage else 0
                }
            else:
                return {
                    'success': False,
                    'error': '图片中未检测到英文文本或文本不清晰',
                    'extracted_text': None
                }
            
        except Exception as e:
            logger.error(f"图片文字识别失败: {str(e)}")
            return {
                'success': False,
                'error': f'图片识别失败: {str(e)}',
                'extracted_text': None
            }
    
    def analyze_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        分析英文文本，判断文体类型（说明文/议论文），然后根据文体结构生成思维导图
        
        Args:
            text (str): 需要分析的英文文本
            
        Returns:
            Dict: 包含分析结果的字典，包括文体类型和思维导图关键词
        """
        try:
            # 构建优化的文体分析提示词
            system_prompt = """你是专业的英文文章分析师。请分析文章的文体类型并生成思维导图关键词。

# 分析步骤

## 第一步：判断文体类型
从以下4种文体类型中选择最符合的一种，下面是各个文体的文章特点，你要根据文章特点来判断文体：

**事实类说明文** - 解释既定事实、概念或现象
- 特征：描述客观存在的事物，回答"是什么"和"怎么样"
- 包括：事物介绍、概念解释、现象说明、技术原理等

**研究类说明文** - 报告科学研究或实验过程  
- 特征：展示新知识的发现过程，回答"为什么"和"如何证明"
- 包括：实验报告、调查研究、数据分析等

**问题解决类说明文** - 分析问题并提出解决方案
- 特征：识别问题、分析原因、提出对策，回答"怎么办"
- 包括：政策建议、改革方案、技术应用等

**议论文** - 提出观点并进行论证
- 特征：表达作者观点，通过论证说服读者，回答"应该怎样"
- 包括：观点论证、价值判断、立场阐述、评论分析等

### 这里是一些例子，议论文：
Ownership used to be about as straightforward as writing a cheque.
If you bought something, you owned it.
If it broke, you fixed it.
If you no longer wanted it, you sold it or threw it away.
In the digital age, however, ownership has become more slippery.
Since the coming of smartphones, consumers have been forced to accept that they do not control the software in their devices; they are only licensed to use it.
As a digital chain is wrapped ever more tightly around more devices, such as cars and thermostats, who owns and who controls which objects is becoming a problem.
Buyers should be aware that some of their most basic property rights are under threat.
The trend is not always harmful.
Manufactures sceking to restrict what owners do with increasingly complex technology have good reasons to protect their copyright, ensure that their machines do not break down, support environmental standards and prevent hacking.
Sometimes companies use their control over a product’s software for the owners’ benefit.
When Hurricane Irma hit Florida this month, Tesla remotely updated the software controlling the batteries of some models to give owners more range to escape the storm.
| But the more digital strings are attached to goods, the more the balance of control leans towards producers and away from owners.
That can be inconvenient.
Picking a car is hard enough, but harder still if you have to dig up the instructions that tell you how use is limited and what data you must give.
If the products are intentionally designed not to last long, it can also be expensive.
Already, items from smartphones to washing machines have become extremely hard to fix, meaning that they are thrown away instead of being repaired.
Privacy is also at risk.
Users become terrified when iRobot, a robotic vacuum cleaner, not only cleans the floor but also creates a digital map of the inside of a home that can then be sold to advertisers (though the manufacturer says it has no intention of doing so).
Cases like this should remind people how jealously they ought to protect their property rights and control who uses the data that is collected.
Ownership is not about to go away, but its meaning is changing.
This requires careful inspection.
Devices, by and large, are sold on the basis that they enable people to do what they want.
To t* extent they are controlled by somebody else, that freedom is compromised.

### 这里是一些例子，事实类说明文：
Most groups of plants and animals are richer in specics and morc plentiful near the equator.
In the ocean, that holds true for cold-blooded predators (x But warm-blooded predators are more diverse toward the poles and noticeably missing from several warm hot spots.
Why?
John Grady, an ecologist, and his team considered the animals need a lot to fuel their metabolism Perhaps colder waters are just richer in small fish?
But they found that at higher, colder places, there isn't actually much more food around, It’s more that warm-blooded animals are eating a much bigger share of it than their cold-blooded competitors.
The real explanation is simple.
An animal’s speed, swiftness, and intelligence depend on its metabolism, which in turn depends on its temperature.
Since birds and mammals can keep heating their bodies in icy conditions, they remain fast and attentive.
By contrast, the fish they hunt become slower and duller, At some tipping point of temperature, seals, dolphins, and penguins start outswimming their prey (49).
They become more likely to come upon targets and outpace the cold-blooded predators of their own.
In Grady’s words, “Warm-blooded predators are favoured where preys are slow, stupid and cold.” That’s why sharks and other predatory fish dominate near the equator, but colder waters are the kingdom of whales and seals.
By keeping food to themselves in the poles, these creatures can then specialize on specific types of prey, which makes them more likely to split into separate species.
The killer whales of the North Pacific, for example, include mammal-eating transients and fish- eating, year-round residents.
But the world is changing.
It’s Jikely that the surface of the oceans will warm by 2 to 3°C within this century.
Grady’s team estimates that every time the ocean's surface warms by 1°C, populations of sca mammals will fall by 12%, and populations of scals and sca lions will fall by 24%.
But “predictions are hard,” Donna Hauser from the University of Alaska Fairbanks notes.
“Polar bears are losers of a warming world, but some populations are still doing well.
Some groups of whales have changed the timing of their migrations; others are hunting in deeper, colder waters.
‘These changes might make sea mammals more adaptable to changing climates.
Maybe they just to find the places where fish remain slow, stupid and cold.”

## 第二步：提取结构关键词
根据文体类型使用对应框架（下面是各个文体的输出的一般结构特点，如果该文体没有对应结构特点，请按照你的理解做合适的结构输出）：

**事实类说明文结构**：引入话题 → 核心定义 → 主要特点 → 分类构成 → 应用意义
**研究类说明文结构**：研究背景 → 研究方法 → 主要发现 → 结论意义  
**问题解决类说明文结构**：问题现状 → 原因分析 → 解决方案 → 效果评估
**议论文结构**：提出论点 → 论证过程 → 反驳质疑 → 总结观点

# 输出格式

## 文体类型
[事实类说明文/研究类说明文/问题解决类说明文/议论文]

## 文章主题
[用1-2个关键词概括文章核心主题]

## 思维导图结构
**中心主题**: [核心关键词]

**主要分支**: 
- 分支1: [关键词]
  - [子分支1]
  - [子分支2]
- 分支2: [关键词]  
  - [子分支1]
  - [子分支2]
- 分支3: [关键词]
  - [子分支1]
  - [子分支2]
- 分支4: [关键词]
  - [子分支1]
  - [子分支2]

**严格格式要求**：
- 主分支以"- "开头
- 子分支以"  - "开头（两个空格+破折号）
- 每个主分支必须有至少2个子分支
- 不要使用"子分支:"这样的标签
- 必须严格按照示例格式输出，不得省略子分支

# 关键要求
1. 关键词简洁精准，每个不超过6个字
2. 突出文章逻辑结构和核心要点
3. 适合制作可视化思维导图
4. 保持层次清晰，便于理解记忆
5. **严格按照格式输出，确保每个主分支都有子分支**

# 输出示例
## 思维导图结构
**中心主题**: 数字时代产权

**主要分支**: 
- 提出论点
  - 产权受威胁
  - 控制权转移
- 论证过程
  - 举例说明
  - 对比分析
- 反驳质疑
  - 承认复杂性
  - 但是转折
- 得出结论
  - 呼吁行动
  - 保护权益"""

            user_prompt = f"""请分析以下英文文章的文体类型和结构，并提取关键词用于制作思维导图。

重要：请严格按照系统提示中的格式要求输出，每个主分支必须包含子分支，子分支以"  - "（两个空格+破折号）开头。

文章内容：
{text}"""
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=1500  # 减少token数量，因为输出更简洁
            )
            
            analysis_result = response.choices[0].message.content
            
            # 解析分析结果并生成思维导图数据
            mindmap_data = self._parse_analysis_to_mindmap(analysis_result, text)
            
            return {
                'success': True,
                'analysis': analysis_result,
                'mindmap_data': mindmap_data,
                'original_text': text,
                'tokens_used': response.usage.total_tokens if response.usage else 0
            }
            
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """测试Azure OpenAI连接"""
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[{"role": "user", "content": "Hello, this is a connection test."}],
                max_tokens=50
            )
            
            return {
                'success': True,
                'message': '连接测试成功',
                'model': self.deployment_name
            }
        except Exception as e:
            logger.error(f"连接测试失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_dynamic_mindmap(self, analysis_text: str, title: str) -> Optional[Dict[str, Any]]:
        """
        从GPT分析结果中动态提取思维导图结构
        
        Args:
            analysis_text (str): GPT分析的结果文本
            title (str): 文章主题
            
        Returns:
            Dict: 思维导图数据结构，如果提取失败返回None
        """
        try:
            lines = analysis_text.split('\n')
            logger.info(f"分析文本总行数: {len(lines)}")
            
            # 查找思维导图结构部分
            in_mindmap_section = False
            branches = []
            current_branch = None
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # 找到思维导图结构开始
                if "思维导图结构" in line or "主要分支" in line:
                    in_mindmap_section = True
                    logger.info(f"第{i+1}行找到思维导图结构开始: {line}")
                    continue
                
                if not in_mindmap_section:
                    continue
                
                # 记录正在处理的行
                if line and not line.startswith('---'):
                    logger.info(f"第{i+1}行处理: '{line}'")
                
                # 跳过空行和分隔符
                if not line or line.startswith('---') or line.startswith('#'):
                    continue
                
                # 检测主分支（以 "- " 开始的行）
                if line.startswith('- ') and not line.startswith('  - '):
                    # 保存之前的分支
                    if current_branch:
                        branches.append(current_branch)
                    
                    # 提取分支标题
                    branch_title = line[2:].strip()
                    if ':' in branch_title:
                        branch_title = branch_title.split(':', 1)[1].strip()
                    branch_title = branch_title.replace('**', '').replace('*', '').strip()
                    
                    current_branch = {
                        "title": branch_title,
                        "children": []
                    }
                    logger.info(f"识别主分支: {branch_title}")
                
                # 检测子分支（以 "  - " 开始，即两个空格+破折号）
                elif line.startswith('  - ') and current_branch is not None:
                    sub_content = line[4:].strip()  # 移除 "  - "
                    
                    # 处理多个子分支在一行的情况（用逗号分隔）
                    if ',' in sub_content:
                        sub_items = [item.strip() for item in sub_content.split(',')]
                        for item in sub_items:
                            if item:
                                current_branch["children"].append({
                                    "title": item,
                                    "children": []
                                })
                                logger.info(f"  添加子分支: {item}")
                    else:
                        if sub_content:
                            current_branch["children"].append({
                                "title": sub_content,
                                "children": []
                            })
                            logger.info(f"  添加子分支: {sub_content}")
            
            # 保存最后一个分支
            if current_branch:
                branches.append(current_branch)
            
            # 如果成功提取到分支结构
            if len(branches) >= 2:
                # 检查是否有子分支
                has_sub_branches = any(len(branch["children"]) > 0 for branch in branches)
                logger.info(f"分支检查结果: 总分支数={len(branches)}, 有子分支={has_sub_branches}")
                
                # 调试：显示每个分支的子分支数量
                for i, branch in enumerate(branches):
                    logger.info(f"分支{i+1}: '{branch['title']}' 有 {len(branch['children'])} 个子分支")
                
                if has_sub_branches:
                    logger.info(f"成功提取到 {len(branches)} 个主分支，包含子分支")
                    return {
                        "title": title,
                        "children": branches
                    }
                else:
                    logger.info(f"提取到 {len(branches)} 个主分支，但无子分支，尝试智能分组")
                    # 尝试智能分组：将过多的主分支重新组织为主分支+子分支结构
                    grouped_branches = self._smart_group_branches(branches)
                    logger.info(f"智能分组完成，生成 {len(grouped_branches)} 个主分支")
                    return {
                        "title": title,
                        "children": grouped_branches
                    }
            else:
                logger.info(f"提取的分支数量不足: {len(branches)}")
                return None
                
        except Exception as e:
            logger.error(f"动态提取思维导图失败: {str(e)}")
            return None
    
    def _smart_group_branches(self, branches: list) -> list:
        """
        智能分组：将过多的主分支重新组织为主分支+子分支结构
        
        Args:
            branches: 原始分支列表
            
        Returns:
            重新组织的分支列表
        """
        try:
            # 如果分支数量合理（4-6个），尝试按照论证结构分组
            if 6 <= len(branches) <= 12:
                # 议论文标准分组：每3个分支为一组
                group_size = 3
                grouped = []
                
                # 定义标准的议论文主分支名称
                main_branch_names = ["提出论点", "进行论证", "反驳质疑", "得出结论"]
                
                for i in range(0, len(branches), group_size):
                    group = branches[i:i+group_size]
                    main_branch_name = main_branch_names[i//group_size] if i//group_size < len(main_branch_names) else f"分支{i//group_size + 1}"
                    
                    # 过滤掉与主分支名称重复的子分支
                    filtered_group = []
                    for branch in group:
                        if branch["title"] != main_branch_name and branch["title"] not in main_branch_name:
                            filtered_group.append(branch)
                    
                    # 如果过滤后没有子分支，保留原始分组但重命名重复项
                    if not filtered_group:
                        filtered_group = group
                        for j, branch in enumerate(filtered_group):
                            if branch["title"] == main_branch_name:
                                branch["title"] = f"{branch['title']}详述"
                    
                    grouped.append({
                        "title": main_branch_name,
                        "children": filtered_group
                    })
                
                logger.info(f"智能分组：{len(branches)}个分支 -> {len(grouped)}个主分支")
                return grouped
            
            # 如果分支过多，简单分组
            elif len(branches) > 12:
                # 每4个为一组
                group_size = 4
                grouped = []
                
                for i in range(0, len(branches), group_size):
                    group = branches[i:i+group_size]
                    group_title = f"主要观点{i//group_size + 1}"
                    
                    # 过滤重复标题
                    filtered_group = []
                    for branch in group:
                        if branch["title"] != group_title:
                            filtered_group.append(branch)
                    
                    # 如果全部过滤掉了，保留原始但重命名
                    if not filtered_group:
                        filtered_group = group
                    
                    grouped.append({
                        "title": group_title,
                        "children": filtered_group
                    })
                
                logger.info(f"简单分组：{len(branches)}个分支 -> {len(grouped)}个主分支")
                return grouped
            
            # 如果分支数量合理，保持原样但添加默认子分支
            else:
                for branch in branches:
                    if len(branch["children"]) == 0:
                        branch["children"] = [
                            {"title": "要点一", "children": []},
                            {"title": "要点二", "children": []}
                        ]
                
                logger.info(f"保持原结构，添加默认子分支")
                return branches
                
        except Exception as e:
            logger.error(f"智能分组失败: {str(e)}")
            return branches
    
    def _parse_analysis_to_mindmap(self, analysis_text: str, original_text: str) -> Dict[str, Any]:
        """
        解析分析结果文本，生成三层思维导图数据结构
        
        Args:
            analysis_text (str): GPT分析的结果文本
            original_text (str): 原始英文文本
            
        Returns:
            Dict: 思维导图数据结构
        """
        try:
            # 基于分析结果中的关键信息构建思维导图
            lines = analysis_text.split('\n')
            
            # 提取文章主题作为中心节点
            title = "文章分析"
            article_type = "议论文"  # 默认类型
            
            # 查找文体类型和主题
            for line in lines:
                if "文体类型" in line or "**议论文**" in line or "**事实类说明文**" in line:
                    if "议论文" in line:
                        article_type = "议论文"
                    elif "说明文" in line:
                        article_type = "说明文"
                elif "文章主题" in line or "中心主题" in line:
                    # 提取主题
                    if ":" in line:
                        title = line.split(":", 1)[1].strip().replace("**", "").replace("*", "")
                    
            # 尝试从GPT分析结果中动态提取思维导图结构
            logger.info("开始动态解析思维导图结构")
            dynamic_mindmap = self._extract_dynamic_mindmap(analysis_text, title)
            
            if dynamic_mindmap:
                logger.info("成功提取动态思维导图结构")
                return dynamic_mindmap
            
            # 如果动态提取失败，使用文体类型模板作为备选
            logger.info("动态提取失败，使用文体类型模板")
            logger.info(f"文体类型判断 - 分析文本包含关键词检查:")
            logger.info(f"  - 包含'议论文': {'议论文' in analysis_text}")
            logger.info(f"  - 包含'事实类说明文': {'事实类说明文' in analysis_text}")
            logger.info(f"  - 包含'研究类说明文': {'研究类说明文' in analysis_text}")
            logger.info(f"  - 包含'问题解决类说明文': {'问题解决类说明文' in analysis_text}")
            
            if "事实类说明文" in analysis_text:
                logger.info("选择事实类说明文结构")
                return self._create_factual_mindmap(analysis_text, title)
            elif "研究类说明文" in analysis_text:
                logger.info("选择研究类说明文结构")
                return self._create_research_mindmap(analysis_text, title)
            elif "问题解决类说明文" in analysis_text:
                logger.info("选择问题解决类说明文结构")
                return self._create_problem_solving_mindmap(analysis_text, title)
            elif "议论文" in analysis_text:
                logger.info("选择议论文结构")
                return self._create_argumentative_mindmap(analysis_text, title)
            else:
                logger.info("未匹配到具体类型，使用默认议论文结构")
                return self._create_argumentative_mindmap(analysis_text, title)
                
        except Exception as e:
            logger.error(f"解析思维导图失败: {str(e)}")
            # 返回默认的三层结构
            return {
                "title": "文章分析",
                "children": [
                    {
                        "title": "主要观点",
                        "children": [
                            {"title": "核心论点", "children": []},
                            {"title": "支撑理由", "children": []}
                        ]
                    },
                    {
                        "title": "论证过程", 
                        "children": [
                            {"title": "事实论据", "children": []},
                            {"title": "对比分析", "children": []}
                        ]
                    },
                    {
                        "title": "结论总结",
                        "children": [
                            {"title": "观点重申", "children": []},
                            {"title": "现实意义", "children": []}
                        ]
                    }
                ]
            }
    
    def _create_argumentative_mindmap(self, analysis_text: str, title: str) -> Dict[str, Any]:
        """创建议论文思维导图"""
        return {
            "title": title,
            "children": [
                {
                    "title": "提出论点",
                    "children": [
                        {"title": "核心观点", "children": []},
                        {"title": "立场表达", "children": []}
                    ]
                },
                {
                    "title": "进行论证",
                    "children": [
                        {"title": "事实论据", "children": []},
                        {"title": "对比分析", "children": []}
                    ]
                },
                {
                    "title": "反驳质疑", 
                    "children": [
                        {"title": "回应异议", "children": []},
                        {"title": "强化观点", "children": []}
                    ]
                },
                {
                    "title": "得出结论",
                    "children": [
                        {"title": "重申观点", "children": []},
                        {"title": "现实意义", "children": []}
                    ]
                }
            ]
        }
    
    def _create_factual_mindmap(self, analysis_text: str, title: str) -> Dict[str, Any]:
        """创建事实类说明文思维导图"""
        return {
            "title": title,
            "children": [
                {
                    "title": "引入话题",
                    "children": [
                        {"title": "现象描述", "children": []},
                        {"title": "背景介绍", "children": []}
                    ]
                },
                {
                    "title": "核心内容",
                    "children": [
                        {"title": "概念定义", "children": []},
                        {"title": "基本特征", "children": []}
                    ]
                },
                {
                    "title": "详细说明",
                    "children": [
                        {"title": "具体表现", "children": []},
                        {"title": "分类构成", "children": []}
                    ]
                },
                {
                    "title": "总结归纳",
                    "children": [
                        {"title": "重要意义", "children": []},
                        {"title": "发展趋势", "children": []}
                    ]
                }
            ]
        }
    
    def _create_research_mindmap(self, analysis_text: str, title: str) -> Dict[str, Any]:
        """创建研究类说明文思维导图"""
        return {
            "title": title,
            "children": [
                {
                    "title": "研究背景",
                    "children": [
                        {"title": "问题提出", "children": []},
                        {"title": "研究意义", "children": []}
                    ]
                },
                {
                    "title": "研究过程",
                    "children": [
                        {"title": "研究方法", "children": []},
                        {"title": "实验步骤", "children": []}
                    ]
                },
                {
                    "title": "研究结果",
                    "children": [
                        {"title": "主要发现", "children": []},
                        {"title": "数据分析", "children": []}
                    ]
                },
                {
                    "title": "研究结论",
                    "children": [
                        {"title": "理论意义", "children": []},
                        {"title": "应用价值", "children": []}
                    ]
                }
            ]
        }
    
    def _create_problem_solving_mindmap(self, analysis_text: str, title: str) -> Dict[str, Any]:
        """创建问题解决类说明文思维导图"""
        return {
            "title": title,
            "children": [
                {
                    "title": "提出问题",
                    "children": [
                        {"title": "问题描述", "children": []},
                        {"title": "问题影响", "children": []}
                    ]
                },
                {
                    "title": "分析原因",
                    "children": [
                        {"title": "主要原因", "children": []},
                        {"title": "次要原因", "children": []}
                    ]
                },
                {
                    "title": "解决措施",
                    "children": [
                        {"title": "核心方案", "children": []},
                        {"title": "配套措施", "children": []}
                    ]
                },
                {
                    "title": "效果展望",
                    "children": [
                        {"title": "预期成效", "children": []},
                        {"title": "实施建议", "children": []}
                    ]
                }
            ]
        } 