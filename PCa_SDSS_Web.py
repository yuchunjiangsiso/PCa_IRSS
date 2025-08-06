import gc
# from datetime import datetime
from owlready2 import *
import uuid
from flask import Flask, request, render_template,jsonify
from markupsafe import Markup  # Flask 内置的安全 HTML 处理库
import calldeepseek
app = Flask(__name__)

# app.extensions['onto'] = onto

@app.route('/')
def entry_page():
    return render_template('index.html')

t_staging_dic = {
    "cT0_1":"cT0",
    "cT1a_1":"cT1a",
    "cT1b_1":"cT1b",
    "cT1c_1":"cT1c",
    "cT2a_1":"cT2a",
    "cT2b_1":"cT2b",
    "cT2c_1":"cT2c",
    "cT3a_1":"cT3a",
    "cT3b_1":"cT3b",
    "cT4_1":"cT4",
    "None":"None"
    }

grade_group_dic ={
    "GradeGroup1_1": "Grade Group 1",
    "GradeGroup2_1": "Grade Group 2",
    "GradeGroup3_1": "Grade Group 3",
    "GradeGroup4_1": "Grade Group 4",
    "GradeGroup5_1": "Grade Group 5",
    "None": "None",
}

risk_group_dic ={
    "RiskVeryLow": "Risk Very Low",
    "RiskLow": "Risk Low",
    "RiskIntermediate": "Risk Intermediate",
    "RiskFavorableIntermediate":"Risk Favorable Intermediate",
    "RiskUnfavorableIntermediate":"Risk Unfavorable Intermediate",
    "RiskHigh":"Risk High",
    "RiskVeryHigh":"Risk Very High"
}

@app.route('/result')
def page_result():

    hasGradeGroup = request.args.get("GradeGroup", "")
    hasTStage = request.args.get("cTNM", "")
    hasPSAValue = request.args.get("PSAValue", "")
    hasPositiveBiospyCoresPercentage = request.args.get("PositiveBiopsyCoresPercentage", "")
    hasPSADensity = request.args.get("PSADensity", "")
    hasCancerPercentageInCore = request.args.get("CancerPercentage", "")
    hasPositiveBiopsyCores = request.args.get("BiopsyCoresPositive", "")

    finalRiskResultDisplay = runReasoner(hasGradeGroup,hasTStage,hasPSAValue,
                hasPositiveBiospyCoresPercentage,hasPSADensity,
                hasCancerPercentageInCore,hasPositiveBiopsyCores)

    html = resultHtml(hasGradeGroup,
    hasTStage,
    hasPSAValue,
    hasPositiveBiospyCoresPercentage,
    hasPSADensity,
    hasCancerPercentageInCore,
    hasPositiveBiopsyCores,
    finalRiskResultDisplay
    )

    return html

def runReasoner(hasGradeGroup,hasTStage,hasPSAValue,
                hasPositiveBiospyCoresPercentage,hasPSADensity,
                hasCancerPercentageInCore,hasPositiveBiopsyCores):

    onto = get_ontology("prostateCancerOntology.owl").load(reload=True)  # reload=True
    # Patient = onto.Patient

    with onto:

        # for individual in list(onto.individuals()):
        #     destroy_entity(individual)

        # 创建新的患者实例
        # patient = Patient("Patient1")
        guid1 = uuid.uuid1()
        patient = onto.Patient(str(guid1))

        if hasGradeGroup != "" and hasGradeGroup != "None":
            patient.hasGradeGroup = [onto[hasGradeGroup]]
        else:
            if hasattr(patient, "hasGradeGroup"):
                del patient.hasGradeGroup  # 完全删除属性关联

        if hasTStage != "" and hasTStage != "None":
            patient.hasTStage = [onto[hasTStage]]
        else:
            if hasattr(patient, "hasTStage"):
                del patient.hasTStage  # 完全删除属性关联

        if hasPSAValue != "":
            patient.hasPSAValue = int(hasPSAValue)
        else:
            if hasattr(patient, "hasPSAValue"):  # 检查属性是否已设置
                del patient.hasPSAValue  # 删除属性关联

        if hasPositiveBiospyCoresPercentage != "":
            patient.hasPositiveBiopsyCoresPercentage = [int(hasPositiveBiospyCoresPercentage)]
        else:
            if hasattr(patient, "hasPositiveBiopsyCoresPercentage"):  # 检查属性是否已设置
                del patient.hasPositiveBiopsyCoresPercentage  # 删除属性关联

        if hasPSADensity != "":
            patient.hasPSADensity = [float(hasPSADensity)]
        else:
            if hasattr(patient, "hasPSADensity"):  # 检查属性是否已设置
                del patient.hasPSADensity  # 删除属性关联

        if hasCancerPercentageInCore != "":
            patient.hasCancerPercentageInCore = [int(hasCancerPercentageInCore)]
        else:
            if hasattr(patient, "hasCancerPercentageInCore"):  # 检查属性是否已设置
                del patient.hasCancerPercentageInCore  # 删除属性关联

        if hasPositiveBiopsyCores != "":
            patient.hasPositiveBiopsyCores = [int(hasPositiveBiopsyCores)]
        else:
            if hasattr(patient, "hasPositiveBiopsyCores"):  # 检查属性是否已设置
                del patient.hasPositiveBiopsyCores  # 删除属性关联

        print(f"创建的患者实例: {patient.name}")
        print("\n推理前的属性值:")
        print(f"hasGradeGroup: {[g.name for g in patient.hasGradeGroup]}")
        print(f"hasTStage: {[t.name for t in patient.hasTStage]}")
        print(
            f"hasPositiveBiopsyCoresPercentage: {patient.hasPositiveBiopsyCoresPercentage} ({type(patient.hasPositiveBiopsyCoresPercentage).__name__})")
        print(f"hasPSAValue: {patient.hasPSAValue} ({type(patient.hasPSAValue).__name__})")
        print(f"hasPSADensity: {patient.hasPSADensity} ({type(patient.hasPSADensity).__name__})")
        print(
            f"hasCancerPercentageInCore: {patient.hasCancerPercentageInCore} ({type(patient.hasCancerPercentageInCore).__name__})")
        print(
            f"hasPositiveBiopsyCores: {patient.hasPositiveBiopsyCores} ({type(patient.hasPositiveBiopsyCores).__name__})")

        # 5. 执行推理
        # close_world(patient)

        from datetime import datetime
        # 记录开始时间
        start_time = datetime.now()
        print(f"start reasoner: {start_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

        sync_reasoner_pellet(onto, debug=False)

        #计算耗时
        end_time = datetime.now()
        elapsed_seconds = (end_time - start_time).total_seconds()

        print(f"end reasoner: {end_time.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        print(f"reasoner elapsed: {elapsed_seconds:.2f} seconds")

        # 6. 检查推理后的类型和属性
        print("\n推理后的类型:")
        for cls in patient.is_a:
            if isinstance(cls, ThingClass):
                print(f"- 命名类: {cls.name}")
            else:
                print(f"- 匿名类: {cls}")

        # 7. 检查风险分类
        risk_classes = [
            onto.RiskVeryLow,
            onto.RiskLow,
            onto.RiskIntermediate,
            onto.RiskFavorableIntermediate,
            onto.RiskUnfavorableIntermediate,
            onto.RiskHigh,
            onto.RiskVeryHigh
        ]

        print("\n风险分类归属:")
        riskResultList = []
        for risk_cls in risk_classes:
            if risk_cls in patient.is_a:
                riskResultList.append(risk_cls.name)

        print(f"推理后属于的类{riskResultList}")

        if "RiskLow" in riskResultList and "RiskVeryLow" in riskResultList:
            finalRiskResult = ["RiskVeryLow"]
            print(f"- 属于风险类: {finalRiskResult}")
        elif "RiskHigh" in riskResultList and "RiskVeryHigh" in riskResultList:
            finalRiskResult = ["RiskVeryHigh"]
            print(f"- 属于风险类: {finalRiskResult}")
        else:
            finalRiskResult = riskResultList
            if (len(riskResultList) > 0):
                print(f"- 属于风险类: {finalRiskResult}")
            else:
                finalRiskResult = ["No Risk Type"]
                print(f"- 属于风险类: 无")

    finalRiskResultDisplay = ",".join(finalRiskResult)
    print(finalRiskResultDisplay)

    onto.destroy()
    gc.collect()

    return finalRiskResultDisplay

@app.route('/api/riskAssessment', methods=['POST'])
def riskAssessment():
    # 获取请求中的JSON数据
    # force=True 表示即使Content-Type不是application/json也尝试解析
    data = request.get_json(force=True)

    hasGradeGroup = data.get('hasGradeGroup','')
    hasTStage = data.get('hasTStage','')
    hasPSAValue = data.get('hasPSAValue', '')
    hasPositiveBiospyCoresPercentage = data.get('hasPositiveBiospyCoresPercentage', '')
    hasPSADensity = data.get('hasPSADensity', '')
    hasCancerPercentageInCore = data.get('hasCancerPercentageInCore', '')
    hasPositiveBiopsyCores = data.get('hasPositiveBiopsyCores', '')

    try:
        finalRiskResultDisplay = runReasoner(hasGradeGroup,hasTStage,hasPSAValue,
                hasPositiveBiospyCoresPercentage,hasPSADensity,
                hasCancerPercentageInCore,hasPositiveBiopsyCores)
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Run reasoner error:{e}',
            'data': None
        }), 400  # 返回400错误状态码

    if ',' in finalRiskResultDisplay:
        finalRiskResultDisplay = finalRiskResultDisplay.split(',')[-1]

    clinicalFeature1 = ""
    try:
        clinicalFeature1 = clinicalFeatures[finalRiskResultDisplay]
    except:
        pass

    initialTherapy1 = ""
    try:
        initialTherapy1 = initialTherapy[finalRiskResultDisplay]
    except:
        pass

    class_to_remove = ' class="list-disc pl-5 space-y-1 text-gray-700"'

    # 构造返回结果
    result = {
        'success': True,
        'message': 'success',
        'data': {
            'risk_group': f'{finalRiskResultDisplay}',
            'clinical_feature': f'{clinicalFeature1.replace(class_to_remove, "")}',
            'initial_therapy': f'{initialTherapy1.replace(class_to_remove, "")}'
        }
    }

    # 返回JSON响应
    return jsonify(result)

clinicalFeatures = {
"RiskVeryLow":Markup("""Has all of the following:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>cT1c</li>
<li>Grade Group 1</li>
<li>PSA <10 ng/mL</li>
<li><3 prostate biopsy fragments/cores positive, ≤50% cancer in each fragment/core</li>
<li>PSA density <0.15 ng/mL/g</li>
</ul>"""),
"RiskLow":Markup("""Has all of the following but does not qualify for very low risk:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>cT1–cT2a</li>
<li>Grade Group 1</li>
<li>PSA <10 ng/mL</li>
</ul>"""),
"RiskIntermediate":Markup("""Has all of the following:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>No high-risk group features</li>
<li>No very-high-risk group features</li>
<li>Has one or more intermediate risk factors (IRFs):</li>
<ul class="list-none pl-5 space-y-1 text-gray-700">
<li class="list-icon-check">cT2b–cT2c</li>
<li class="list-icon-check">Grade Group 2 or 3</li>
<li class="list-icon-check">PSA 10–20 ng/mL</li>
</ul>
</ul>"""),
"RiskFavorableIntermediate":Markup("""Has all of the following:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>1 IRF</li>
<li>Grade Group 1 or 2</li>
<li><50% biopsy cores positive (eg, <6 of 12 cores)</li>
</ul>"""),
"RiskUnfavorableIntermediate":Markup("""Has one or more of the following:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>2 or 3 IRFs</li>
<li>Grade Group 3</li>
<li>≥50% biopsy cores positive (eg, ≥ 6 of 12 cores)</li>
</ul>"""),
"RiskHigh":Markup("""Has one or more high-risk features, but does not meet criteria for very high risk:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>cT3–cT4</li>
<li>Grade Group 4 or Grade Group 5</li>
<li>PSA >20 ng/mL</li>
</ul>"""),
"RiskVeryHigh":Markup("""Has at least two of the following: 
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>cT3–cT4</li>
<li>Grade Group 4 or 5</li>
<li>PSA >40 ng/mL</li>
</ul>""")}

initialTherapy = {
"RiskVeryLow":Markup("""
For patients with an expected survival of ≥ 10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Active surveillance</li>
</ul>
For patients with an expected survival of < years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Observation</li>
</ul>
"""),
"RiskLow":Markup("""
For patients with an expected survival of ≥ 10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Active surveillance</li>
<li>Radiation therapy (RT)</li>
<li>Radical prostatectomy (RP)</li>
</ul>
For patients with an expected survival of < years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Observation</li>
</ul>
"""),
"RiskIntermediate":Markup("""
Favorable Intermediate-Risk Group:<br />
For patients with an expected survival of >10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Active surveillance</li>
<li>Radical prostatectomy (RP)</li>
<li>Radiation therapy (RT)</li>
</ul>
For patients with an expected survival of 5–10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radiation therapy (RT)</li>
<li>Observation</li>
</ul>
<br />
Unfavorable Intermediate-Risk Group:<br />
For patients with an expected survival of >10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radical prostatectomy (RP)</li>
<li>Radiation therapy (RT) + androgen deprivation therapy (ADT) for 4–6 months</li>
</ul>
For patients with an expected survival of 5–10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radiation therapy (RT) + androgen deprivation therapy (ADT) for 4–6 months</li>
<li>Observation</li>
</ul>
"""),
"RiskFavorableIntermediate":Markup("""
For patients with an expected survival of >10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Active surveillance</li>
<li>Radical prostatectomy (RP)</li>
<li>Radiation therapy (RT)</li>
</ul>
For patients with an expected survival of 5–10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radiation therapy (RT)</li>
<li>Observation</li>
</ul>
"""),
"RiskUnfavorableIntermediate":Markup("""
For patients with an expected survival of > 10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radical prostatectomy (RP)</li>
<li>Radiation therapy (RT) + androgen deprivation therapy (ADT) for 4–6 months</li>
</ul>
For patients with an expected survival of 5–10 years, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radiation therapy (RT) + androgen deprivation therapy (ADT) for 4–6 months</li>
<li>Observation</li>
</ul>
"""),
"RiskHigh":Markup("""
For patients with an expected survival of > 5 years or who are symptomatic, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radiation therapy (RT) + androgen deprivation therapy (ADT) for 12–36 months</li>
<li>Radical prostatectomy (RP)</li>
</ul>
For patients with an expected survival of ≤5 years and who are asymptomatic, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Observation</li>
<li>Radiation therapy (RT)</li>
<li>Androgen deprivation therapy (ADT) with or without Radiation therapy (RT)</li>
</ul>
"""),
"RiskVeryHigh":Markup("""
For patients with an expected survival of > 5 years or who are symptomatic, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Radiation therapy (RT) + androgen deprivation therapy (ADT) for 12–36 months</li>
<li>Radiation therapy (RT) + androgen deprivation therapy (ADT) for 24 months + abiraterone</li>
<li>Radical prostatectomy (RP)</li>
</ul>
For patients with an expected survival of ≤5 years and who are asymptomatic, the recommended initial therapeutic options are as follows:
<ul class="list-disc pl-5 space-y-1 text-gray-700">
<li>Observation</li>
<li>Radiation therapy (RT)</li>
<li>Androgen deprivation therapy (ADT) with or without Radiation therapy (RT)</li>
</ul>
""")}

def resultHtml(hasGradeGroup,
    hasTStage,
    hasPSAValue,
    hasPositiveBiospyCoresPercentage,
    hasPSADensity,
    hasCancerPercentageInCore,
    hasPositiveBiopsyCores,
    finalRiskResultDisplay):

    # 处理多个的情况，取Risk高的那个
    if ',' in finalRiskResultDisplay:
        finalRiskResultDisplay = finalRiskResultDisplay.split(',')[-1]

    clinicalFeature1 = ""
    try:
        clinicalFeature1 = clinicalFeatures[finalRiskResultDisplay]
    except:
        pass

    initialTherapy1 = ""
    try:
        initialTherapy1 = initialTherapy[finalRiskResultDisplay]
    except:
        pass

    if hasGradeGroup in grade_group_dic.keys():
        hasGradeGroup = grade_group_dic[hasGradeGroup]

    if hasTStage in t_staging_dic.keys():
        hasTStage = t_staging_dic[hasTStage]

    #组装内容给deepseek
    clinicalFeaures1 = "";
    if hasPSAValue != "":
        clinicalFeaures1 += f"""PSA Value (ng/mL): {hasPSAValue} ng/mL \n"""

    if hasPositiveBiopsyCores != "":
        clinicalFeaures1 += f"""Positive Prostate Biopsy Cores: {hasPositiveBiopsyCores} \n"""

    if hasCancerPercentageInCore != "":
        clinicalFeaures1 += f"""Cancer Percentage in Each Core (%): {hasCancerPercentageInCore} \n"""

    if hasPSADensity != "":
        clinicalFeaures1 += f"""PSA Density (ng/mL/g): {hasPSADensity} ng/mL/g \n"""

    if hasPositiveBiospyCoresPercentage != "":
        clinicalFeaures1 += f"""Percentage of Positive Biopsy Cores (%): {hasPositiveBiospyCoresPercentage} ng/mL/g \n"""

    if finalRiskResultDisplay in risk_group_dic.keys():
        finalRiskResultDisplay = risk_group_dic[finalRiskResultDisplay]


    deepSeekResult = calldeepseek.callDeepSeek(clinicalFeaures1, finalRiskResultDisplay)
    deepSeekResult = deepSeekResult.replace("<ul>", '<ul class="list-disc pl-5 space-y-1 text-gray-700">').replace('<ol>','<ol class="list-decimal">')

    print(deepSeekResult)

    recommendTherapy1 = Markup(deepSeekResult)

    print(recommendTherapy1)

    return render_template('submit_result.html',
                           hasGradeGroup=hasGradeGroup,
                           hasTStage=hasTStage,
                           hasPSAValue=hasPSAValue,
                           hasPositiveBiospyCoresPercentage=hasPositiveBiospyCoresPercentage,
                           hasPSADensity=hasPSADensity,
                           hasCancerPercentageInCore=hasCancerPercentageInCore,
                           hasPositiveBiopsyCores=hasPositiveBiopsyCores,
                           finalRiskResultDisplay=finalRiskResultDisplay,
                           clinicalFeature = clinicalFeature1,
                           initialTherapy = initialTherapy1,
                           recommendTherapy = recommendTherapy1)

    return html

import werkzeug.serving
werkzeug.serving.run_simple("localhost", 5000, app)