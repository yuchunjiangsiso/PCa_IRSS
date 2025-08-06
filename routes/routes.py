# routes.py - 路由模块
import random

from flask import Flask,Blueprint, render_template,request,current_app
from markupsafe import Markup  # Flask 内置的安全 HTML 处理库
from owlready2 import *

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/result', methods=['GET', 'POST'])
def page_result():
    finalRiskResult = ""

    # onto = current_app.extensions['onto']
    onto = get_ontology("prostateCancerOntology.owl").load()
    Patient = onto.Patient

    with onto:
        hasGradeGroup = request.args.get("GradeGroup", "")
        hasTStage = request.args.get("cTNM", "")
        hasPSAValue = request.args.get("PSAValue", "")
        hasPositiveBiospyCoresPercentage = request.args.get("PositiveBiopsyCoresPercentage", "")
        hasPSADensity = request.args.get("PSADensity", "")
        hasCancerPercentageInCore = request.args.get("CancerPercentage", "")
        hasPositiveBiopsyCores = request.args.get("BiopsyCoresPositive", "")

        # 创建新的患者实例
        patientName = random.randint(1,10000)
        #patient = Patient("Patient1")
        patient = Patient(str(patientName))

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
        sync_reasoner_pellet(onto)

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

        # print("\n风险分类归属:")
        # riskResultList = []
        # for risk_cls in risk_classes:
        #     if patient in risk_cls.instances():
        #         # print(f"- 属于风险类: {risk_cls.name}")
        #         riskResultList.append(risk_cls.name)

        print("\n风险分类归属:")
        riskResultList = []
        for risk_cls in risk_classes:
            if risk_cls in patient.is_a:
                riskResultList.append(risk_cls.name)

        print(riskResultList)

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

    # html = """<html><body>
    # <h3>Result: %s</h3>
    # </body></html>""" % ",".join(finalRiskResult)

    finalRiskResultDisplay = ",".join(finalRiskResult)
    print(finalRiskResultDisplay)

    html = resultHtml(hasGradeGroup,
                      hasTStage,
                      hasPSAValue,
                      hasPositiveBiospyCoresPercentage,
                      hasPSADensity,
                      hasCancerPercentageInCore,
                      hasPositiveBiopsyCores,
                      finalRiskResultDisplay
                      )

    onto.destroy()
    return html

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
                           initialTherapy = initialTherapy1)

    return html

