from openai import OpenAI
import markdown  # 用于转换Markdown格式（如 * 加粗）
from markupsafe import Markup  # Flask 内置的安全 HTML 处理库

client = OpenAI(api_key="sk-03ce3fd1d3624ec2a6bed1da73e6009c", base_url="https://api.deepseek.com")

# 将带 * 的文本转换为HTML
def format_response(text):
    # 转换Markdown语法（如 *...* → <em>...</em>, **...** → <strong>...</strong>）
    print(text)
    html_content = markdown.markdown(text)
    print(html_content)
    return html_content

clinicalFeaures ="""
PSA Value (ng/mL): 8 ng/mL
Positive Prostate Biopsy Cores: 2
Cancer Percentage in Each Core (%): 35%
PSA Density (ng/mL/g): 0.12 ng/mL/g
Grade Group: Grade Group 1
Clinical T-Staging: cT1c
"""
riskGroup = """
Risk Very Low
"""

def callDeepSeek(clinicalFeatures1,riskGroup1):
    global clinicalFeaures,riskGroup

    clinicalFeaures = clinicalFeatures1
    riskGroup = riskGroup1

    if riskGroup=="No Risk Type":
        return "No risk stratification is available, therefore no treatment recommendations can be made."

    info = f"""
    The clinical and pathological features of this prostate cancer patient are as follows:
    {clinicalFeaures}
    The risk level of this prostate cancer patient is:
    Risk Group: 
    {riskGroup}

    Based on the information provided above, provide treatment recommendations.
    """

    from datetime import datetime

    # 记录开始时间
    start_time = datetime.now()
    print(f"start deepseek request: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    # 调用DeepSeek API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a specialist in prostate cancer treatment."},
            {"role": "user", "content": f"{info}"}
        ],
        stream=False
    )

    # 计算耗时
    end_time = datetime.now()
    elapsed_seconds = (end_time - start_time).total_seconds()

    print(f"end deepseek request: {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    print(f"deepseek request elapsed: {elapsed_seconds:.2f} seconds")

    return format_response(response.choices[0].message.content)

# a="""
# PSA Value (ng/mL): 8 ng/mL
# Positive Prostate Biopsy Cores: 2
# Cancer Percentage in Each Core (%): 35%
# PSA Density (ng/mL/g): 0.12 ng/mL/g
# Grade Group: Grade Group 1
# Clinical T-Staging: cT1c
# """
# b="""
# Risk Very Low
# """
# print(Markup(callDeepSeek(a,b).replace("<ul>",'<ul class="list-disc pl-5 space-y-1 text-gray-700">')))

