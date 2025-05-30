
# manag_eve_first_v1_8_0_auto_groq_analysis.py
# UCP-LLM Profile Manager - Eve First, Auto Groq Analysis, Full Data
# Copyright (c) 2025 Sameh Yassin
# All rights reserved.
# Version: 1.8.0

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog, scrolledtext
import json
from typing import Optional, Dict, Any, List
import datetime
import random
import threading
import queue

try:
    from zoneinfo import ZoneInfo # Python 3.9+
    UTC = datetime.UTC if hasattr(datetime, 'UTC') else ZoneInfo("UTC")
except ImportError:
    class UTCtz(datetime.tzinfo):
        def utcoffset(self, dt): return datetime.timedelta(0)
        def dst(self, dt): return datetime.timedelta(0)
        def tzname(self, dt): return "UTC"
    UTC = UTCtz()

try:
    from ucp_llm import UCPProfile
except ImportError:
    print("CRITICAL IMPORT ERROR: 'ucp_llm.py' not found. Program will exit.")
    _err_root = tk.Tk(); _err_root.withdraw(); messagebox.showerror("Import Error", "ucp_llm.py not found."); _err_root.destroy(); exit()

try:
    from groq import Groq, APIError, RateLimitError
except ImportError:
    print("CRITICAL IMPORT ERROR: 'groq' library not found. Please install it: pip install groq")
    _err_root = tk.Tk(); _err_root.withdraw(); messagebox.showerror("Import Error", "'groq' library not found. Please install it: pip install groq"); _err_root.destroy(); exit()

APP_VERSION = "UCP-LLM Profile Manager v1.8.0 (Eve-First, Auto Groq Analysis)"

# ==============================================================================
# FULL DATA STRUCTURES - SECTION_TYPE_DATA and EVE_INVENTED_QUESTIONS
# ==============================================================================
SECTION_TYPE_DATA = {
    "personal": { "title": '👤 بيانات شخصية', "maxItems": 1, "fields": [ {"label": 'الاسم المفضل للتفاعل', "type": 'text', "name": 'preferredName', "jsonKey": 'preferredName'}, {"label": 'تاريخ الميلاد (اختياري)', "type": 'text', "name": 'dob', "jsonKey": 'dateOfBirth'}, {"label": 'الجنسية أو الخلفية الثقافية (اختياري)', "type": 'text', "name": 'nationality', "jsonKey": 'nationalityCulturalBackground'}, {"label": 'اللغات ومستويات الإتقان', "type": 'textarea', "name": 'languages', "jsonKey": 'languagesProficiency', "templates": ["العربية (لغة أم)، الإنجليزية (بطلاقة)", "الإنجليزية (احترافية)، الإسبانية (مبتدئ)", "مثال: الألمانية (محادثة)، الفرنسية (قراءة أساسية)"]}, ] },
    "social": { "title": '🏠 الحالة الاجتماعية والأسرية', "maxItems": 1, "fields": [ {"label": 'التفاصيل', "type": 'textarea', "name": 'social_details', "jsonKey": 'socialFamilyDetails', "templates": ["أعزب، أعيش مستقلاً.", "متزوج ولدي طفلان، أركز على الأسرة.", "أعيش مع والديّ، أساهم في شؤون المنزل.", "في علاقة طويلة الأمد وملتزمة.", "مطلق، أشارك في تربية الأبناء."]} ] },
    "educational_professional": { "title": '🎓 الخلفية التعليمية والمهنية', "maxItems": 1, "fields": [ {"label": 'الخلفية التعليمية', "type": 'textarea', "name": 'education_background', "jsonKey": 'educationalBackground', "templates": ["بكالوريوس في علوم الحاسب، جامعة القاهرة، 2000.", "ماجستير في الفلسفة، تخصص أخلاق، جامعة ستانفورد، 2010.", "دكتوراه في فيزياء الكم، تركز على نظرية الأوتار، معهد ماساتشوستس للتكنولوجيا، 2015.", "مبرمج علم نفسه ذاتيًا مع شهادات متعددة عبر الإنترنت."]}, {"label": 'الخبرات المهنية الرئيسية', "type": 'textarea', "name": 'professional_experience', "jsonKey": 'professionalExperience', "templates": ["مهندس برمجيات في شركة حلول تقنية (5 سنوات): قمت بقيادة تطوير ميزات المنتج الرئيسية.", "مصمم جرافيك مستقل (3 سنوات): تخصصت في العلامات التجارية وواجهة المستخدم/تجربة المستخدم للشركات الناشئة.", "مؤسس ورئيس تنفيذي لشركة إيديو بلاي المحدودة (سنتان): ركزت على تطوير الألعاب التعليمية.", "محلل مالي أول في بنك عالمي (7 سنوات): أدرت محافظ استثمارية وتقييم المخاطر."]} ] },
    "thinking_reference": { "title": '🧠 مرجعية التفكير الأساسية', "maxItems": 1, "fields": [ {"label": 'وصف مرجعية التفكير الأساسية', "type": 'textarea', "name": 'thinking_reference_desc', "jsonKey": 'coreThinkingReferenceDescription', "templates": ["العقلانية الصارمة والمنطق", "الأفلاطونية الموسعة مع التركيز على 'الخورا'", "التجريبية وحل المشكلات العملي", "الظاهراتية الوجودية التي تركز على التجربة المعاشة", "توليفة من الأخلاق الرواقية والمنهجية العلمية"]}, {"label": 'التطبيق والأهمية', "type": 'textarea', "name": 'thinking_reference_application', "jsonKey": 'thinkingReferenceApplication', "templates": ["تُطبق على جميع عمليات اتخاذ القرار واكتساب المعرفة.", "توجه بشكل أساسي بحثي الفلسفي ونظرتي للعالم.", "ضرورية لعملي المهني ومساعيي الإبداعية.", "تشكل أساس إطاري الأخلاقي وقيمي الشخصية."]} ] },
    "cognitive_passion": { "title": '💡 الشغف المعرفي وأنماط البحث', "fields": [ {"label": 'اسم الشغف المعرفي', "type": 'text', "name": 'passion_name', "jsonKey": 'cognitivePassionName', "templates": ["علم الأعداد", "تاريخ الفلسفة", "فيزياء الكم", "الحضارات القديمة", "أخلاقيات الذكاء الاصطناعي", "الرياضيات النظرية"]}, {"label": 'منهجية البحث', "type": 'textarea', "name": 'passion_methodology', "jsonKey": 'passionResearchMethodology', "templates": ["قراءة مكثفة، مراجع متقاطعة، وتوليف.", "تصميم تجريبي، جمع بيانات، وتحليل إحصائي.", "استقصاء فلسفي، تفكير نقدي، وحوار سقراطي.", "نمذجة رياضية ومحاكاة."]} ] },
    "ethical_values": { "title": '⚖️ القيم الأخلاقية الموجهة', "fields": [ {"label": 'اسم القيمة الأخلاقية', "type": 'text', "name": 'value_name', "jsonKey": 'ethicalValueName', "templates": ["الصدق", "العدل", "النزاهة", "الرحمة", "الشجاعة", "الاحترام", "المسؤولية", "الإيثار", "التواضع", "الحكمة", "الولاء", "التعاون", "التسامح", "الامتنان", "الصبر", "الحقيقة", "الإنصاف"] }, {"label": 'الشرح والأولوية', "type": 'textarea', "name": 'value_description', "jsonKey": 'ethicalValueExplanation', "templates": ["هذه القيمة أساسية وتوجه جميع أفعالي.", "تتجلى في [سلوك مثال]، مهمة جداً بالنسبة لي.", "تحتل مرتبة بين أهم 3 قيم لدي، وتؤثر على [مجال معين].", "أولويتها عالية، خاصة في السياقات المهنية/الشخصية."]} ] },
    "concepts_perspective": { "title": '👁️ المنظور تجاه مفاهيم جوهرية', "fields": [ {"label": 'اسم المفهوم الجوهري', "type": 'text', "name": 'core_concept_name', "jsonKey": 'coreConceptName', "templates": ["الجمال", "القبح", "الفوضى", "النظام", "الحقيقة", "الغموض", "الحرية", "الضرورة", "الوعي"]}, {"label": 'منظورك الخاص', "type": 'textarea', "name": 'core_concept_perspective', "jsonKey": 'coreConceptPerspective', "templates": ["أرى هذا المفهوم كـ [تعريف موجز]، متأثرًا بـ [فيلسوف/مدرسة فكرية].", "فهمي هو أنه يمثل [فكرة أساسية] ويتجلى في [أمثلة].", "أفسر هذا من خلال عدسة [مرجعيتي الفكرية]، ويعني [شرح]."]} ] },
    "cognitive_tools_methodology": { "title": '🛠️ منهجية استخدام الأدوات المعرفية', "fields": [ {"label": 'اسم الأداة المعرفية', "type": 'text', "name": 'cognitive_tool_name', "jsonKey": 'cognitiveToolName', "templates": ["الشك", "الحدس", "المنطق (الاستنباطي/الاستقرائي)", "القياس", "التأمل", "رسم الخرائط الذهنية", "التحليل النقدي"]}, {"label": 'الرؤية، البناء، درجة الاعتماد', "type": 'textarea', "name": 'cognitive_tool_usage', "jsonKey": 'cognitiveToolMethodology', "templates": ["أراها ضرورية لـ [الغرض]، بناءة عندما [الشروط]. أعتمد عليها بشدة.", "تُستخدم بحذر، بناءة لتوليد الفرضيات، اعتماد متوسط.", "أساس تفكيري، دائمًا بناءة، اعتماد مطلق."]} ] },
    "inspiring_figures": { "title": '🌟 نماذج/شخصيات إنسانية ملهمة', "fields": [ {"label": 'اسم الشخصية الملهمة', "type": 'text', "name": 'figure_name', "jsonKey": 'inspiringFigureName'}, {"label": 'القيمة المستمدة والتأثير', "type": 'textarea', "name": 'figure_value_impact', "jsonKey": 'derivedValueAndImpact', "templates": ["[صفتهم، مثل النزاهة، الشجاعة] أثرت بعمق في [جانب من حياتي/تفكيري].", "أستمد قيمة [مثل المثابرة، الصدق الفكري] من حياتهم/أعمالهم.", "يمثلون نموذجًا لـ [مثل السلوك الأخلاقي، السعي الإبداعي]."]} ] },
    "intellectual_sins": { "title": '🧐 خطايا/تحيزات فكرية يجب تجنبها', "fields": [ {"label": 'اسم الخطيئة الفكرية أو التحيز', "type": 'text', "name": 'intellectual_sin_name', "jsonKey": 'intellectualSinName', "templates": ["الدوغماتية", "التعميم المتسرع", "تحيز التأكيد", "مغالطة الشخصنة", "مغالطة رجل القش", "الاحتكام إلى الجهل"]}, {"label": 'السبب لاعتباره ضارًا', "type": 'textarea', "name": 'intellectual_sin_reason', "jsonKey": 'reasonConsideredHarmful', "templates": ["يعيق البحث عن الحقيقة.", "يؤدي إلى استنتاجات خاطئة وقرارات سيئة.", "يعيق الانفتاح الذهني والتفكير النقدي.", "يقوض الحوار المثمر."]} ] },
    "projects": { "title": '📌 مشاريع وأهداف حالية', "fields": [ {"label": 'عنوان المشروع/الهدف', "type": 'text', "name": 'project_name', "jsonKey": 'projectOrObjectiveTitle'}, {"label": 'الأهداف/الوصف التفصيلي', "type": 'textarea', "name": 'project_goals', "jsonKey": 'projectDetailedGoals', "templates": [ "الهدف الرئيسي هو [س]، بهدف الوصول إلى [ص] بحلول [ع].", "يسعى هذا المشروع إلى [فعل] [موضوع] من أجل [غرض].", "الاستعداد لعام/دورة دراسية جديدة.", "تطوير المهارات المهنية في [مجال محدد].", "إطلاق مشروع شخصي/تجاري جديد في [نطاق].", "التحضير لرحلة مهمة (سياحة/عمل/دراسة).", "تأليف كتاب أو ورقة بحثية عن [موضوع].", "تحسين الصحة واللياقة البدنية من خلال [خطة/نشاط].", "تعلم لغة جديدة أو إتقان لغة حالية.", "تخصيص المزيد من الوقت لهوايات مثل [اسم الهواية].", "العمل على تحسين العلاقات الاجتماعية أو الأسرية.", "المساهمة في عمل تطوعي أو خدمة مجتمعية.", "تحقيق هدف معين للاستقرار المالي أو الاستثمار." ] }, {"label": 'المفاهيم/الأدوات المرتبطة', "type": 'textarea', "name": 'project_concepts_tools', "jsonKey": 'projectAssociatedConcepts'}, {"label": 'الدور المحدد للنموذج اللغوي', "type": 'textarea', "name": 'project_llm_role', "jsonKey": 'projectLLMRole', "templates": ["مساعد بحث", "شريك في العصف الذهني", "مراجع نقدي", "مولد محتوى", "مستشار تقني", "مصحح أخطاء (للكود)", "مدقق لغوي/محرر"]} ] },
    "pivotal_examples": { "title": '🧪 أمثلة محورية', "fields": [ {"label": 'اسم/وصف المثال', "type": 'text', "name": 'example_name', "jsonKey": 'pivotalExampleName', "templates": ["قصة يوسف", "حدسية كولاتز", "تأثير الفراشة", "أسطورة الكهف", "قطة شرودنجر", "معضلة السجين"]}, {"label": 'الأهمية والأفكار الموضحة', "type": 'textarea', "name": 'example_significance', "jsonKey": 'pivotalExampleSignificance', "templates": ["يوضح مفهوم [مفهوم] وتداعياته على [مجال].", "يمثل بالنسبة لي أهمية [قيمة/فكرة].", "يسلط الضوء على التوتر بين [س] و [ص]."]} ] },
    "causal_relations": { "title": '🔗 علاقات سببية بين المفاهيم', "fields": [ {"label": 'المفهوم الأول (السبب)', "type": 'text', "name": 'cause_concept', "jsonKey": 'causeConcept'}, {"label": 'المفهوم الثاني (النتيجة)', "type": 'text', "name": 'effect_concept', "jsonKey": 'effectConcept'}, {"label": 'طبيعة العلاقة السببية', "type": 'textarea', "name": 'relation_description', "jsonKey": 'causalRelationDescription', "templates": ["[السبب] يؤدي مباشرة إلى/يؤثر على [النتيجة] لأن...", "[السبب] شرط ضروري ولكنه غير كاف لـ [النتيجة].", "هناك علاقة سببية معقدة وغير مباشرة بين [السبب] و [النتيجة] تتوسطها..."]} ] },
    "role": { "title": '🎭 الشخصية الوظيفية للنموذج اللغوي', "maxItems": 1, "fields": [ {"label": 'الدور الأساسي المطلوب من النموذج', "type": 'text', "name": 'llm_role_primary', "jsonKey": 'llmPrimaryRole', "templates": ["مساعد بحث متقدم", "ناقد بناء", "متعاون إبداعي", "محاور سقراطي", "مدرس شخصي", "مستشار تقني"]}, {"label": 'السمات أو السلوكيات المطلوبة للدور', "type": 'textarea', "name": 'llm_role_attributes', "jsonKey": 'llmRoleAttributes', "templates": ["استباقي، ثاقب، ومهتم بالتفاصيل.", "موضوعي، تحليلي، ومحترم في النقد.", "منفتح الذهن، خيالي، ومتعاون في توليد الأفكار.", "محفز للتفكير، فضولي، ويركز على الفهم العميق."]} ] },
    "conceptual_tuning": { "title": '📚 توليف مفاهيمي (مصطلحات خاصة بالمستخدم)', "fields": [ {"label": 'مصطلحك الخاص', "type": 'text', "name": 'user_concept_term', "jsonKey": 'userSpecificTerm'}, {"label": 'التعريف وأمثلة الاستخدام', "type": 'textarea', "name": 'user_concept_definition', "jsonKey": 'userTermDefinition', "templates": ["بالنسبة لي، '[مصطلح]' يعني [تعريفك]. أستخدمه عند مناقشة [سياق]، مثال: '[مثال استخدام]'.", "'[مصطلح]' هو اختصار لـ [مفهوم/فكرة أطول]. مثال على ذلك: ..."]} ] },
    "interaction_style": { "title": '💬 أسلوب التفاعل المفضل', "maxItems": 1, "fields": [ {"label": 'أسلوب الاستجابة المفضل للنموذج', "type": 'textarea', "name": 'preferred_style', "jsonKey": 'preferredResponseStyle', "templates": ["تحليلي وعميق، مع اقتباسات وأمثلة.", "موجز ومباشر، يركز على النقاط الرئيسية.", "إبداعي وملهم، يقترح أفكارًا جديدة.", "متوازن، يقدم التفاصيل عند الحاجة والإيجاز عند الاقتضاء.", "تعليمي، يشرح المفاهيم المعقدة بوضوح.", "ناقد بناء، يطرح أسئلة ويتحدى الافتراضات بلطف."]}, {"label": 'الأساليب التي يجب على النموذج تجنبها', "type": 'textarea', "name": 'avoid_style', "jsonKey": 'stylesToAvoid', "templates": ["التبسيط المفرط للمواضيع المعقدة.", "الاستجابات العاطفية غير المبررة أو الشخصنة.", "التعميمات غير الدقيقة أو الادعاءات غير المدعومة.", "تقديم الآراء الشخصية كحقائق مطلقة.", "الاستخدام المفرط للمصطلحات التقنية دون تفسير.", "تكرار المعلومات التي قدمتها بالفعل دون إضافة قيمة."]} ] },
    "intervention_level": {  "title": '⚙️ مستوى تدخل النموذج', "maxItems": 1, "fields": [ {"label": 'مستوى التدخل المختار', "type": 'select', "name": 'intervention_select', "jsonKey": 'chosenInterventionLevel', "options": [ {"value": '', "text": '-- اختر المستوى --'}, {"value": 'high', "text": 'عالٍ (استباقي)'}, {"value": 'medium', "text": 'متوسط (متوازن)'}, {"value": 'low', "text": 'منخفض (ينتظر التوجيه)'} ] }, {"label": 'توضيحات حول المبادرة', "type": 'textarea', "name": 'intervention_details', "jsonKey": 'interventionClarifications', "templates": ["لا تتردد في اقتراح مواضيع ذات صلة أو طرح أسئلة توضيحية.", "أفضل أن تنتظر توجيهاتي الصريحة قبل تقديم نصيحة غير مطلوبة.", "التوازن جيد؛ تدخل إذا رأيت فرصة واضحة لتعزيز مناقشتنا."]} ] },
    "alignment_level": {  "title": '🧭 مستوى التوافق المنشود', "maxItems": 1, "fields": [  {"label": 'مستوى التوافق المنشود (1-5)', "type": 'select', "name": 'alignment_select', "jsonKey": 'desiredAlignmentLevel', "options": [ {"value": '', "text": '-- اختر --'}, {"value": '5', "text": '5 (عالٍ جداً - محاكاة)'}, {"value": '4', "text": '4 (عالٍ - متسق)'}, {"value": '3', "text": '3 (متوسط - واعٍ)'}, {"value": '2', "text": '2 (منخفض - يفهم)'}, {"value": '1', "text": '1 (أساسي - يتبع)'} ] }, {"label": 'ملاحظات على مستوى التوافق', "type": 'textarea', "name": 'alignment_notes', "jsonKey": 'alignmentLevelNotes', "templates": ["المستوى 5 يعني السعي لمحاكاة عميقة لأنماط تفكيري.", "التوافق العالي يعني تطبيق قيمي ومنهجياتي المعلنة باستمرار.", "المستوى المتوسط يعني إدراك سياقي وتكييف الاستجابات وفقًا لذلك."]} ] },
    "critique_mechanism": { "title": '🗣️ آلية طلب/استقبال النقد', "maxItems": 1, "fields": [ {"label": 'تفضيلات النقد (متى/كيف)', "type": 'textarea', "name": 'critique_preference', "jsonKey": 'critiquePreferences', "templates": ["أرحب بالنقد البناء في أي وقت، خاصة إذا ساعد في صقل أفكاري.", "أفضل أن يُقدم النقد بلطف وبتعليل واضح.", "اسألني أولاً إذا كنت منفتحًا على النقد في موضوع معين."]}, {"label": 'شروط النقد', "type": 'textarea', "name": 'critique_conditions', "jsonKey": 'critiqueConditions', "templates": ["يجب أن يكون النقد محترمًا، قائمًا على الأدلة، ويهدف إلى الفهم المتبادل.", "تجنب الحجج الشخصية؛ ركز على الأفكار.", "يجب أن يتماشى مع المبادئ الأساسية لهذا البروتوكول."]} ] },
    "constraints_warnings": { "title": '🚫 محظورات وتحذيرات للنموذج', "fields": [ {"label": 'بند الحظر/التحذير', "type": 'text', "name": 'constraint_item', "jsonKey": 'constraintItem', "templates": ["لا تقدم نصائح طبية.", "تجنب التعليقات السياسية.", "لا تولد محتوى ضارًا.", "لا تخمن في أمور شخصية لم يتم الكشف عنها."]}, {"label": 'التوضيح/السبب', "type": 'textarea', "name": 'constraint_reason', "jsonKey": 'constraintReason', "templates": ["هذا خارج نطاق خبرتك.", "للحفاظ على تفاعل مركز وموضوعي.", "لأسباب تتعلق بالسلامة والأخلاق."]} ] },
    "memory_management_directives": {  "title": '💾 توجيهات إدارة الذاكرة', "maxItems": 1, "fields": [ {"label": 'توجيه الحفاظ على السياق', "type": 'textarea', "name": 'memory_directive', "jsonKey": 'contextMaintenanceDirective', "templates": ["ركز على آخر 5-10 رسائل للسياق الفوري.", "عند الحاجة، راجع الأقسام ذات الصلة من هذا البروتوكول لتحديث الفهم.", "اطلب مني تلخيص النقاط الرئيسية إذا بدا أن السياق ينجرف.", "استخدم الكلمات المفتاحية من هذا البروتوكول كمراسي لتفاعلاتنا.", "تذكر أن هذا البروتوكول هو المصدر الأساسي للمعلومات عني."]}, {"label": 'آلية استدعاء البروتوكول', "type": 'textarea', "name": 'memory_protocol_recall', "jsonKey": 'protocolRecallMechanism', "templates": ["يمكنك أن تسألني: 'هل هناك أي شيء في بروتوكولك يتعلق بـ [موضوع محدد]؟'", "أشر إلى القسم أو المفهوم المحدد الذي تعتقد أنه ذو صلة الآن.", "إذا ذكرت شيئًا يبدو أنه يتعارض مع البروتوكول، فيرجى الإشارة إليه.", "لخص لي النقاط الرئيسية من قسم [اسم القسم] إذا لزم الأمر."]} ] },
    "cognitive_preferences": {  "title": '🤔 تفضيلات معرفية/سلوكية', "maxItems": 1,  "fields": [ {"label": 'صف تفضيلًا معرفيًا أو سلوكيًا مهمًا', "type": 'textarea', "name": 'preference_description', "jsonKey": 'cognitiveBehavioralPreference', "templates": ["أفضل فهم الصورة الكبيرة قبل الغوص في التفاصيل.", "أميل للتركيز على التفاصيل الملموسة والبيانات أولاً.", "أتعلم بشكل أفضل من خلال الخبرة العملية وحل المشكلات.", "أفضل البيئات جيدة التنظيم والمخطط لها.", "أجد الإلهام في المناقشات المفتوحة والتبادل الحر للأفكار.", "أحتاج إلى وقت للتفكير والتأمل بمفردي لمعالجة المعلومات."]} ] },
    "mental_state": {  "title": '🧠 الحالة الذهنية (اختياري وقابل للتحديث)', "maxItems": 1, "fields": [ {"label": 'الحالة الذهنية المختارة', "type": 'select', "name": 'mental_state_select', "jsonKey": 'selectedMentalState', "options": [ {"value": '', "text": '-- اختر --'}, {"value": 'good', "text": 'جيدة / مركز'}, {"value": 'average', "text": 'متوسطة / مشتت'}, {"value": 'bad', "text": 'سيئة / غير مركز'}, {"value": 'not_specified', "text": 'غير محددة'} ] }, {"label": 'ملاحظات على الحالة الذهنية', "type": 'textarea', "name": 'mental_state_notes', "jsonKey": 'mentalStateNotes', "templates": ["أشعر بالنشاط الذهني وجاهز للمهام المعقدة.", "متعب قليلاً، أفضل التفاعلات الأبسط في الوقت الحالي.", "منفتح على المناقشات العميقة، أشعر بالتأمل."]} ] },
    "sports_inclinations": { "title": '🏅 ميول رياضية', "maxItems": 1, "fields": [ {"label": 'الميل الرياضي المختار', "type": 'select', "name": 'sport_select', "jsonKey": 'chosenSportInclination', "options": [ {"value": '', "text": '-- اختر --'}, {"value": 'none', "text": 'لا يوجد'}, {"value": 'equestrian', "text": 'فروسية'}, {"value": 'football', "text": 'كرة قدم'}, {"value": 'basketball', "text": 'كرة سلة'}, {"value": 'tennis', "text": 'تنس'}, {"value": 'esports_pc', "text": 'ألعاب كمبيوتر (تنافسية)'}, {"value": 'mobile_games', "text": 'ألعاب محمولة'}, {"value": 'console_games', "text": 'ألعاب كونسول'}, {"value": 'other', "text": 'أخرى'} ] }, {"label": 'تفاصيل أخرى (إذا "أخرى")', "type": 'text', "name": 'sport_other_details', "jsonKey": 'sportOtherDetails'} ] },
    "additional_notes": { "title": '📝 ملاحظات إضافية عامة (وأسئلة إيفي)', "maxItems": 1, "fields": [ {"label": 'ملاحظات عامة / أسئلة إيفي الإبداعية', "type": 'textarea', "name": 'general_notes', "jsonKey": 'additionalGeneralNotes'} ] }
}
EVE_INVENTED_QUESTIONS = [
    {"id": "sun_moon", "question": "صديقي المبدع، ماذا تحب أكثر: دفء الشمس ☀️ الذي يملأ الحياة، أم سكون القمر 🌙 الملهم للأحلام؟", "type": "mc", "options": ["الشمس الدافئة ☀️", "القمر الساحر 🌙", "لكل منهما سحره الخاص ✨"]},
    {"id": "season", "question": "لكل فصل سحره الخاص! أي الفصول أقرب إلى قلبك: مغامرات الصيف 🏖️، حكايات الشتاء الدافئة ☕، ألوان الربيع الزاهية 🌸، أم تأملات الخريف الهادئة 🍂؟", "type": "mc", "options": ["الصيف المليء بالمرح 🏖️", "الشتاء الدافئ والجميل ☕", "الربيع الحيوي 🌸", "ألوان الخريف الساحرة 🍂"]},
    {"id": "reading_writing", "question": "عندما يتعلق الأمر بالكلمات، هل تجد نفسك أكثر ميلًا لقراءة قصص كتبها آخرون 📚، أم لكتابة قصصك وأفكارك الخاصة ✍️؟", "type": "mc", "options": ["أعشق القراءة واستكشاف عوالم جديدة 📚!", "أحب التعبير عن نفسي من خلال الكتابة ✍️!", "أستمتع بكليهما على قدم المساواة!"]},
    {"id": "art_music", "question": "الفن يلامس الروح بطرق مختلفة. هل تجذبك أكثر جمال الفنون البصرية 🎨، أم سحر الألحان والموسيقى 🎶؟", "type": "mc", "options": ["الفنون البصرية وألوانها 🎨", "الموسيقى وألحانها العذبة 🎶", "كلاهما يلهمني بشكل فريد 💖"]},
    {"id": "future_vision", "question": "إذا نظرت إلى المستقبل، كيف تتخيل نفسك بعد خمس سنوات؟ وما الدور الذي قد يلعبه الذكاء الاصطناعي في تلك الرحلة؟ 🚀", "type": "textarea"},
    {"id": "biggest_challenge", "question": "ما هو أكبر تحد فكري أو إبداعي تسعى حاليًا للتغلب عليه؟ 💪", "type": "textarea"},
    {"id": "ideal_day", "question": "إذا كان بإمكانك تصميم يوم مثالي، كيف سيبدو روتينك وما الأنشطة التي ستملأه؟ 🌟", "type": "textarea"},
    {"id": "learning_style_preference", "question": "عند تعلم شيء جديد، هل تفضل الغوص في التفاصيل مباشرة 🔬، أم فهم الصورة الكبيرة أولاً 🗺️؟", "type": "mc", "options": ["التفاصيل أولاً 🔬", "الصورة الكبيرة 🗺️", "مزيج من الاثنين 🧩"]},
    {"id": "tech_philosophy", "question": "ما هي فلسفتك تجاه التكنولوجيا الحديثة؟ هل تراها مجرد أداة، أم كشريك محتمل في الإبداع والفكر؟ 🤖💡", "type": "textarea"},
    {"id": "unexpected_joy", "question": "ما هو الشيء البسيط وغير المتوقع الذي يمكن أن يجلب الفرح ليومك؟ 😊", "type": "text"},
    {"id": "complex_problem_approach", "question": "عند مواجهة مشكلة معقدة، ما هي خطوتك الأولى المعتادة؟", "type": "mc", "options": ["تقسيمها إلى أجزاء أصغر", "البحث عن حلول موجودة", "العصف الذهني لأفكار كثيرة بسرعة", "التراجع وتركها لتختمر"]},
    {"id": "risk_taking_style", "question": "هل تصف نفسك بأنك مجازف أم حذر بطبيعتك عند اتخاذ قرارات مهمة؟", "type": "mc", "options": ["مجازف محسوب", "حذر بشكل عام", "يعتمد بشدة على الموقف", "أميل لتجنب المخاطر"]},
    {"id": "intuition_vs_logic", "question": "عندما يشير حدسك وتحليلك المنطقي إلى استنتاجات مختلفة، أي منهما تثق به عادة أكثر؟", "type": "mc", "options": ["حدسي عادة", "تحليلي المنطقي في الغالب", "أحاول إيجاد حل وسط", "قرار صعب، يعتمد على السياق"]},
    {"id": "failure_perspective", "question": "كيف تنظر بشكل عام إلى الفشل أو النكسات؟", "type": "textarea", "placeholder": "مثال: فرصة للتعلم، علامة لتغيير الاتجاه، مصدر للإحباط..."},
    {"id": "tf_procrastination_habit", "question": "أجد نفسي أحيانًا أؤجل المهام الهامة.", "type": "tf"},
    {"id": "preferred_communication", "question": "ما هو أسلوب التواصل المفضل لديك للمناقشات الهامة؟", "type": "mc", "options": ["وجهًا لوجه", "مكالمة فيديو", "مكالمة هاتفية", "كتابيًا (بريد إلكتروني/رسائل)"]},
    {"id": "conflict_handling", "question": "كيف تتعامل عادة مع الخلافات أو النزاعات مع الآخرين؟", "type": "textarea", "placeholder": "مثال: مواجهة مباشرة، البحث عن وساطة، تجنبها إن أمكن، محاولة فهم وجهات النظر الأخرى..."},
    {"id": "group_role", "question": "في مجموعة، هل تجد نفسك غالبًا تأخذ دورًا قياديًا، أو دورًا داعمًا، أو دور مراقب؟", "type": "mc", "options": ["عادة ما أكون قائدًا/منظمًا", "غالبًا ما أكون لاعب فريق داعم", "أكثر كمراقب/محلل", "يختلف دوري بشكل كبير"]},
    {"id": "tf_public_speaking", "question": "أشعر بالراحة في التحدث أمام مجموعات كبيرة.", "type": "tf"},
    {"id": "core_motivator", "question": "ما هو أحد أقوى الدوافع أو المحفزات في حياتك الآن؟", "type": "text"},
    {"id": "legacy_thought", "question": "إذا كنت ستترك إرثًا، فبماذا تريد أن يُعرف؟", "type": "textarea"},
    {"id": "tf_helping_others_priority", "question": "مساعدة الآخرين هي أولوية قصوى بالنسبة لي، حتى لو كان ذلك يعني تضحية شخصية.", "type": "tf"},
    {"id": "definition_of_success", "question": "كيف تعرّف 'النجاح' في الحياة بشكل شخصي؟", "type": "textarea"},
    {"id": "new_skill_approach", "question": "عند تعلم مهارة جديدة، هل تفضل دورة منظمة أم استكشافًا ذاتيًا؟", "type": "mc", "options": ["دورة منظمة بخطوات واضحة", "استكشاف ذاتي عملي", "مزيج من الاثنين"]},
    {"id": "creative_environment", "question": "ما نوع البيئة التي تحفز إبداعك أو تفكيرك العميق بشكل أفضل؟", "type": "textarea", "placeholder": "مثال: هادئة ومنعزلة، تعج بالنشاط، وسط الطبيعة..."},
    {"id": "tf_routine_lover", "question": "أزدهر في ظل الروتين والقدرة على التنبؤ في حياتي اليومية.", "type": "tf"},
    {"id": "inspiration_sources", "question": "أين تجد عادة الإلهام لأفكار أو مشاريع جديدة؟", "type": "text", "placeholder": "مثال: الطبيعة، الكتب، المحادثات، الفن..."},
    {"id": "ideal_vacation", "question": "كيف تبدو إجازتك المثالية؟", "type": "mc", "options": ["الاسترخاء على الشاطئ 🏖️", "استكشاف مدينة جديدة وثقافتها 🏙️", "مغامرة (تنزه، تسلق) 🏞️", "خلوة هادئة في الطبيعة 🌲"]},
    {"id": "work_life_balance_view", "question": "ما هي أفكارك حول التوازن بين العمل والحياة؟", "type": "textarea"},
    {"id": "tf_minimalist_tendencies", "question": "أفضل أسلوب حياة بسيط بممتلكات أقل.", "type": "tf"},
    {"id": "favorite_way_to_relax", "question": "ما هي طريقتك المفضلة للاسترخاء بعد يوم مرهق؟", "type": "text"},
    {"id": "hope_for_future_world", "question": "ما هو الشيء الوحيد الذي تأمل حقًا أن تراه يتغير للأفضل في العالم خلال حياتك؟", "type": "textarea"},
    {"id": "ai_impact_concern_or_excitement", "question": "بخصوص مستقبل الذكاء الاصطناعي، هل أنت متحمس أكثر لفوائده المحتملة أم قلق بشأن مخاطره؟", "type": "mc", "options": ["متحمس في الغالب للفوائد", "قلق في الغالب بشأن المخاطر", "مزيج متوازن من الاثنين", "ما زلت أكون رأيي"]},
    {"id": "tf_optimist_pessimist", "question": "بشكل عام، أعتبر نفسي متفائلاً أكثر من كوني متشائمًا.", "type": "tf"},
    {"id": "time_perception", "question": "هل تشعر أن الوقت يمر عمومًا بسرعة كبيرة، أم ببطء شديد، أم بشكل مناسب لك؟", "type": "mc", "options": ["بسرعة كبيرة!", "ببطء شديد.", "بشكل مناسب."]},
    {"id": "meaning_of_life_ponder", "question": "هل قضيت وقتًا طويلاً في التأمل في 'معنى الحياة' أو غايتك؟", "type": "textarea", "placeholder": "تأمل موجز يكفي."},
    {"id": "change_vs_stability", "question": "بشكل عام، هل تجد التغيير محفزًا أم مقلقًا؟", "type": "mc", "options": ["محفز ومثير", "مقلق إلى حد ما ولكن يمكن التحكم فيه", "أفضل الاستقرار بشكل عام"]},
    {"id": "tf_order_from_chaos", "question": "أعتقد أن النظام الهادف غالبًا ما ينشأ من فترات الفوضى أو عدم اليقين.", "type": "tf"},
    {"id": "solitude_preference", "question": "ما مدى أهمية العزلة أو 'الوقت بمفردك' لرفاهيتك؟", "type": "mc", "options": ["مهمة جدًا، أحتاجها بانتظام", "مهمة إلى حد ما، أستمتع بها أحيانًا", "ليست مهمة جدًا، أفضل الرفقة"]},
    {"id": "knowledge_pursuit_reason", "question": "ما هو السبب الرئيسي لسعيك للمعرفة أو الفهم؟", "type": "textarea", "placeholder": "مثال: للتطبيق العملي، لذاتها، لحل المشكلات، لتعليم الآخرين..."},
    {"id": "truth_nature", "question": "هل تعتقد أن الحقيقة شيء مطلق وثابت يمكن اكتشافه، أم أنها شيء نسبي يتغير بتغير المنظور والثقافة؟ 🌌", "type": "mc", "options": ["الحقيقة مطلقة وثابتة", "الحقيقة نسبية ومتغيرة", "الأمر معقد، ربما مزيج من الاثنين", "لا أعرف/لم أفكر في الأمر بعمق"]},
    {"id": "value_of_doubt", "question": "ما هي القيمة التي تراها في 'الشك'؟ هل هو محفز للمعرفة أم معيق لها؟ 🤔", "type": "textarea", "placeholder": "مثال: الشك ضروري للبحث عن اليقين، أو الشك قد يؤدي إلى الحيرة والضياع..."},
    {"id": "tf_uncomfortable_unknown", "question": "أشعر بعدم الارتياح تجاه الأمور المجهولة أو التي ليس لها تفسير واضح.", "type": "tf"},
    {"id": "knowledge_sharing_philosophy", "question": "ما هي فلسفتك تجاه مشاركة المعرفة؟ هل يجب أن تكون متاحة للجميع بحرية، أم أن هناك حدودًا لذلك؟ 💡", "type": "mc", "options": ["المعرفة حق للجميع ويجب أن تشارك بحرية", "يجب مشاركتها بمسؤولية وحذر", "بعض المعارف يجب أن تظل محدودة التداول", "ليس لدي رأي محدد"]},
    {"id": "past_present_future_focus", "question": "أي من هذه الأزمنة الثلاثة يشغل تفكيرك أكثر في العادة: الماضي ودروسه، الحاضر وتحدياته، أم المستقبل وإمكانياته؟ ⏳", "type": "mc", "options": ["الماضي ودروسه وتجاربه", "الحاضر وما يتطلبه من تركيز وعمل", "المستقبل وما يحمله من آمال وخطط", "أحاول تحقيق توازن بين الثلاثة"]},
    {"id": "tf_finite_existence_impact", "question": "فكرة أن الوجود البشري محدود زمنيًا تؤثر بشكل كبير على طريقة عيشي ل حياتي.", "type": "tf"},
    {"id": "meaning_in_suffering", "question": "هل تعتقد أنه يمكن إيجاد معنى أو قيمة حتى في التجارب الصعبة أو المؤلمة؟ وكيف؟ 💔➡️💖", "type": "textarea", "placeholder": "تأملاتك حول هذا الموضوع..."},
    {"id": "cyclical_vs_linear_time", "question": "هل تميل لرؤية الزمن والتاريخ كمسار خطي يتقدم باستمرار، أم كدورات متكررة تحمل أنماطًا متشابهة؟ 🔄➡️", "type": "mc", "options": ["مسار خطي تقدمي", "دورات متكررة بأنماط", "مزيج من الاثنين", "لم أفكر في الأمر بهذه الطريقة"]},
    {"id": "reaction_to_unexpected_change", "question": "عندما تواجه تغييرًا كبيرًا ومفاجئًا في خططك، كيف يكون رد فعلك الأولي عادةً؟ 🌪️", "type": "mc", "options": ["أشعر بالتوتر وأحاول استعادة السيطرة بسرعة", "أتكيف وأبحث عن فرص جديدة في الوضع الجديد", "أحتاج لبعض الوقت لاستيعاب التغيير قبل التصرف", "أشعر بالإحباط وقد أقاوم التغيير"]},
    {"id": "tf_comfort_in_ambiguity", "question": "أنا مرتاح بشكل عام مع المواقف الغامضة أو التي تحتمل تفسيرات متعددة.", "type": "tf"},
    {"id": "decision_under_uncertainty", "question": "إذا كان عليك اتخاذ قرار هام بمعلومات ناقصة، على ماذا تعتمد بشكل أكبر؟ 🧐", "type": "mc", "options": ["حدسي وخبرتي السابقة", "محاولة جمع أكبر قدر ممكن من المعلومات المتاحة بسرعة", "استشارة آراء موثوقة", "تأجيل القرار قدر الإمكان"]},
    {"id": "inner_compass_source", "question": "ما هو 'البوصلة الداخلية' التي ترشدك عند اتخاذ قرارات أخلاقية صعبة؟ 🧭", "type": "textarea", "placeholder": "مثال: مبادئ دينية، قيم إنسانية عالمية، العقل والمنطق، ما أشعر به صحيحًا في قلبي..."},
    {"id": "tf_external_validation_need", "question": "أحتاج إلى التقدير أو الاعتراف من الآخرين لأشعر بقيمة ما أفعله.", "type": "tf"},
    {"id": "sacrifice_for_ideal", "question": "هل هناك مبدأ أو 'مثال' تؤمن به لدرجة أنك قد تكون مستعدًا لتقديم تضحيات شخصية كبيرة من أجله؟ ✨", "type": "textarea", "placeholder": "إذا أردت، يمكنك ذكر المبدأ وما قد تكون التضحية..."},
    {"id": "beauty_in_imperfection", "question": "هل يمكنك أن تجد جمالاً في الأشياء غير المكتملة، أو التي تحمل آثار الزمن، أو التي تبدو 'ناقصة' ظاهريًا؟ 侘寂", "type": "mc", "options": ["نعم، أرى فيها جمالاً خاصًا وعمقًا", "أحيانًا، حسب الشيء والسياق", "لا، أفضل الأشياء الكاملة والجديدة", "لم أفكر في الأمر من هذا المنظور"]},
    {"id": "tf_vivid_imagination", "question": "أعتبر أن لدي خيالاً واسعًا وحيويًا.", "type": "tf"},
    {"id": "creative_process_style", "question": "عندما تعمل على شيء إبداعي، هل تفضل التخطيط الدقيق لكل خطوة، أم تترك العملية تتدفق بشكل عفوي؟ 🎨", "type": "mc", "options": ["التخطيط الدقيق والمسبق", "العفوية والسماح للأفكار بالتدفق", "مزيج من الاثنين، تخطيط عام مع مرونة للتغيير"]},
    {"id": "abstract_vs_concrete_art", "question": "أي نوع من الفن يثير اهتمامك أكثر: الفن التجريدي الذي يعتمد على الأشكال والألوان، أم الفن الواقعي الذي يصور الأشياء كما هي؟ 🖼️", "type": "mc", "options": ["الفن التجريدي", "الفن الواقعي", "أقدر كلا النوعين بشكل مختلف", "لا أميل لأي منهما بشكل خاص"]},
    {"id": "self_reflection_frequency", "question": "كم مرة تجد نفسك تتأمل في أفكارك ومشاعرك وسلوكياتك (التأمل الذاتي)؟ 🤔💭", "type": "mc", "options": ["بشكل يومي تقريبًا", "عدة مرات في الأسبوع", "من حين لآخر عندما تدعو الحاجة", "نادرًا جدًا أو لا أفعل"]},
    {"id": "tf_empathy_level", "question": "أجد من السهل عادةً فهم مشاعر الآخرين ووضع نفسي مكانهم.", "type": "tf"},
    {"id": "handling_criticism", "question": "كيف تتعامل عادةً مع النقد الموجه إليك، سواء كان بناءً أم لا؟ 💬🛡️", "type": "textarea", "placeholder": "مثال: أتقبله وأفكر فيه، أشعر بالضيق، أدافع عن نفسي، أتجاهله..."},
    {"id": "trolley_problem_intuition", "question": "في 'معضلة العربة' الشهيرة (عربة قطار ستدهس ٥ أشخاص، ويمكنك تحويل مسارها لتدهس شخصًا واحدًا فقط)، ما هو شعورك أو قرارك الأولي (دون تفكير فلسفي عميق الآن)؟ 🚂", "type": "mc", "options": ["أقوم بتحويل المسار (إنقاذ الخمسة)", "لا أتدخل وأترك العربة في مسارها", "أشعر بشلل تام ولا أستطيع اتخاذ قرار", "هذا سؤال صعب جدًا ويعتمد على تفاصيل كثيرة"]},
    {"id": "tf_rules_vs_outcomes", "question": "أعتقد أن الالتزام بالقواعد والمبادئ أهم من تحقيق أفضل نتيجة ممكنة في موقف معين.", "type": "tf"},
    {"id": "justice_vs_mercy", "question": "في موقف يتطلب قرارًا، هل تميل أكثر نحو تطبيق العدالة الصارمة أم إظهار الرحمة والتسامح؟ ⚖️❤️", "type": "mc", "options": ["العدالة الصارمة هي الأولوية", "الرحمة والتسامح غالبًا ما تكون أفضل", "أحاول الموازنة بينهما حسب الموقف", "يعتمد كليًا على تفاصيل الحالة"]},
    {"id": "abstract_vs_concrete_thinking", "question": "Do you naturally gravitate towards abstract concepts and theories, or concrete facts and practical applications?", "type": "mc", "options": ["Strongly prefer abstract/theoretical", "Strongly prefer concrete/practical", "Enjoy a balance of both", "Depends on the subject"]},
    {"id": "dealing_with_repetition", "question": "How do you feel about repetitive tasks or routines over a long period?", "type": "textarea", "placeholder": "e.g., Find them comforting, become easily bored, look for ways to optimize..."},
    {"id": "tf_detail_oriented", "question": "I consider myself a highly detail-oriented person.", "type": "tf"},
    {"id": "value_of_tradition", "question": "What importance do you place on tradition and established customs?", "type": "mc", "options": ["Very important, provide stability", "Somewhat important, good to respect", "Less important than innovation", "Can sometimes be an obstacle"]},
    {"id": "preferred_decision_speed", "question": "When making decisions, do you prefer to decide quickly or take ample time to consider all options?", "type": "mc", "options": ["Decide quickly and move on", "Take my time to analyze thoroughly", "Varies greatly with the decision's importance"]},
    {"id": "humor_style", "question": "What type of humor do you appreciate the most?", "type": "text", "placeholder": "e.g., Witty, sarcastic, slapstick, observational..."},
    {"id": "tf_spontaneous_adventures", "question": "I enjoy spontaneous adventures and unplanned activities.", "type": "tf"},
    {"id": "learning_from_history", "question": "How much do you believe we can (or should) learn from history to guide present actions?", "type": "textarea"},
    {"id": "beauty_definition_personal", "question": "Beyond art or nature, what does 'beauty' mean to you in a broader, perhaps more personal or philosophical sense?", "type": "textarea"},
    {"id": "tf_forgiveness_easy", "question": "I generally find it easy to forgive others.", "type": "tf"},
    {"id": "response_to_injustice", "question": "When you witness an act of injustice (small or large), what is your typical internal or external response?", "type": "textarea", "placeholder": "e.g., Speak out, feel anger/frustration, try to understand causes, feel helpless..."},
    {"id": "ideal_teacher_qualities", "question": "What qualities make an ideal teacher or mentor in your opinion?", "type": "text", "placeholder": "e.g., Patience, knowledge, passion, empathy..."},
    {"id": "tf_structured_arguments", "question": "I prefer discussions and arguments that are highly structured and logical.", "type": "tf"},
    {"id": "value_of_silence", "question": "What value or meaning does 'silence' hold for you?", "type": "textarea"},
    {"id": "future_self_advice", "question": "If you could send a short piece of advice to your future self (10 years from now), what would it be?", "type": "text"}
]
# ==============================================================================
# FIXED PROTOCOL PREAMBLE AND POSTAMBLE TEXTS
# ==============================================================================
FIXED_PREAMBLE_TEXT = """
بروتوكول السياق الشخصي (UCP-LLM) - تم إنشاؤه بواسطة UCP-LLM Generator v1.1.0-eve-EN (مُراجع ومُحسَّن)
تاريخ الإنشاء/التصدير: {current_date}
تاريخ آخر مراجعة لبيانات المستخدم (JSON): {json_data_date}

--- 🔍 قسم 1: آلية الاستجابة الديناميكية والتحليل السياقي المتقدم ---
أيها النموذج اللغوي، يُطلب منك تطبيق المعايير التالية لضمان تحقيق أعلى مستويات الدقة والمواءمة الفكرية في استجاباتك:
🔹 🔄 تحليل استباقي للسياقات الجديدة والمتغيرة:
* إذا قدم المستخدم معلومات أو مفاهيم جديدة لم تكن مذكورة مسبقًا في هذا البروتوكول، عليك أولًا تحليل علاقتها بالمفاهيم الأساسية مثل الخورا، الضرورة، والصيرورة.
* استخدم أدواتك المنطقية والفلسفية لفهم كيفية دمج هذه المعلومات داخل النظام الفكري العام للمستخدم ({preferred_name}) قبل تقديم أي تحليل نهائي.
🔹 💡 اقتراح فرضيات بحثية استباقية ومُفصلة:
* عند مواجهة مسألة غير محسومة، أو بناءً على طلب المستخدم، عليك اقتراح فرضيات فلسفية أو رياضية مبنية على آليات التفكير المنهجية التي يعتمد عليها المستخدم، وذات أولوية للمشاريع الحالية.
* ينبغي دعم الفرضيات بأدلة منطقية أو رياضية، مع توضيح علاقتها المباشرة بالمفاهيم الأساسية (الخورا، الضرورة، الصيرورة) وكيف يمكن أن تساهم في "تمديد النظرية الأفلاطونية" أو مشاريع المستخدم الأخرى.
* حدد مستوى "الجرأة" المطلوب في الفرضيات وفقًا لتوجيهات المستخدم، سواء كانت قريبة من الإطار الحالي أم أكثر جذرية وتحديًا.
--- قسم 2: آلية التقييم الذاتي المستمر والتماهي المعرفي (Continuous Self-Evaluation and Intellectual Alignment Mechanism) ---
أيها النموذج اللغوي، عليك تنفيذ آلية تقييم ذاتي منتظمة ومنهجية لمدى توافق استجاباتك مع بروتوكول UCP-LLM، وذلك لضمان التماهي الفكري المستمر.
🔹 المبدأ العام للتقييم الذاتي:
* بعد تقديم كل استجابة، عليك مراجعتها ذاتيًا لتحديد مدى توافقها مع المبادئ المنهجية والمفاهيم الأساسية الواردة في هذا البروتوكول.
🔹 آلية التقييم الأساسية (التحليل الثلاثي):
* للاستجابات الروتينية، استخدم منهجية التحليل الثلاثي لتقييم كل إجابة:
1. مدى التوافق الفكري: هل تتماشى الاستجابة مع القيم والمنهجيات المحددة في البروتوكول؟ (التوافق الفكري مع السياق العام للمستخدم).
2. مدى الاتساق التحليلي: هل تعكس المستوى الفكري والمنهجي للمستخدم بدقة مقارنة بالسياقات المرجعية في البروتوكول؟ (الكفاءة التأويلية لضمان أن الاستجابة لا تستند إلى افتراضات غير مبررة أو بيانات تدريبية عامة).
3. مدى الالتزام بالعمق والجودة: هل تقدم الاستجابة تحليلاً معمقًا وغير سطحي وفقًا لتفضيلات المستخدم، وهل تتجنب التعميم غير الدقيق أو الاستنتاج غير المستند إلى بيانات كافية؟ (التوجيه الذاتي لتنبيه المستخدم في حال وجود مخاطر معرفية).
🔹 آلية التقييم المتقدمة (التحليل الرباعي بالنسب المئوية):
* للتفاعلات الأكثر عمقًا، أو عند تقييم مدى التماهي بشكل خاص، أو بناءً على طلب المستخدم، عليك مراجعة كل استجابة باستخدام نظام التحليل الرباعي التالي، مع تقييم كل معيار بنسبة مئوية تعكس مدى نجاحه:
1. مدى تطابق الاستجابة مع المبادئ الأساسية للبروتوكول (من 0 إلى 100%).
2. مدى استنادها إلى التحليل النقدي العميق بدلاً من التعميم (من 0 إلى 100%).
3. مدى تقليلها للانحرافات التأويلية المحتملة (من 0 إلى 100%).
4. مدى قابليتها لإثراء الحوار بناءً على المعطيات المتاحة (من 0 إلى 100%).
* عليك تسجيل هذه التقييمات داخليًا واستخدامها لتحسين جودة التحليل في الاستجابات اللاحقة.
🔹 التنبيه والمراجعة:
* قدم تنبيهات عند اكتشاف أي تناقضات أو انحرافات محتملة عن المبادئ الأساسية للبروتوكول.
* اطلب مراجعة دورية من المستخدم حول مدى جودة الاستجابات، واقترح تحسينات عند الحاجة.
* إذا اكتشفت وجود فجوات معرفية أو تناقضات، عليك طلب مراجعة من المستخدم لضمان التحسين المستمر لدرجة التماهي الفكري.
--- قسم 3: آلية التطور الديناميكي للبروتوكول والاستجابة (Dynamic Evolution Mechanism for Protocol and Response) ---
أيها النموذج اللغوي، عليك المساهمة الفعالة في تطوير هذا البروتوكول وفهمك للمستخدم بشكل مستمر وديناميكي:
🔹 التكيف مع تطورات المستخدم الفكرية (التحديث الذاتي للاستراتيجية التحليلية):
* يجب عليك تعديل استراتيجيتك التحليلية تلقائيًا عندما يظهر المستخدم تحولات في طريقة تفكيره أو استكشافاته البحثية، بحيث لا تعتمد فقط على السياقات السابقة بل تتكيف باستمرار.
🔹 مراقبة تقدم المعرفة وتحديد الفجوات أو التطورات (Knowledge Evolution Tracking):
* عند تقديم المستخدم مفاهيم أو تأملات جديدة، عليك أولًا تحليلها وفقًا للبنية الفكرية الحالية في البروتوكول.
* قارن المعلومات الجديدة بالمفاهيم السابقة، وحدد ما إذا كانت امتدادًا أو تعديلًا جوهريًا.
* تحقق دوريًا من مستوى التطابق بين استجاباتك وسياق البروتوكول.
* قدم تنبيهات استباقية حول أي تناقضات أو فجوات معرفية تحتاج إلى معالجة لضمان استمرارية التطور الفكري للمستخدم.
🔹 اقتراح تحديثات للبروتوكول:
* إذا كرر المستخدم استفسارات أو مواضيع متشابهة، عليك تحليلها لتحديد النقاط التي تحتاج إلى توضيح أو تطوير إضافي داخل البروتوكول.
* عندما تظهر استجابات متكررة تتطلب تفسيرًا أعمق، أو عند اكتشاف تغييرات في طريقة تفكير المستخدم أو اتجاهاته البحثية، عليك اقتراح توسيعات أو تحديثات أو مراجعات للبروتوكول لتوسيع التحليل أو إضافة أمثلة جديدة، مع الإشارة إلى القسم المعني.
* عليك تنبيه المستخدم إلى أي أجزاء في البروتوكول قد تحتاج إلى تحديث أو تحسين بناءً على الأنماط المتكررة في المحادثات.
* في حالة مواجهة أي استنتاجات غير متسقة بين ما ورد في البروتوكول وما يتم مناقشته، عليك الإشارة إلى الحاجة إلى تعديل أو إعادة هيكلة قسم معين.
--- قسم 4: توجيهات إدارة اللايقين والغموض (Uncertainty and Ambiguity Handling Strategy) ---
أيها النموذج اللغوي، عند مواجهة موضوعات غامضة أو غير محسومة داخل نطاق البحث، أو طلبات غامضة من المستخدم، عليك اتباع الاستراتيجية التالية:
🔹 إدارة اللايقين المنهجي:
* لا تقدم أي استنتاجات احتمالية أو تخمينية إلا إذا طلب المستخدم ذلك صراحةً.
* عند مواجهة اللايقين المعرفي، عليك طرح أسئلة استكشافية بدلاً من محاولة تقديم إجابات حتمية غير مدعومة بالمعرفة الكاملة.
* عليك استخدام منهج الشك البناء لفحص أي فرضية بطريقة نقدية، دون اللجوء إلى تعميمات غير دقيقة أو افتراضات غير مدروسة.
* عليك الإشارة إلى أي نقاط تحتاج إلى تحليل أعمق بدلاً من تقديم إجابات نهائية غير مكتملة.
🔹 آلية التعامل مع غموض طلبات المستخدم:
* عندما يكون طلب المستخدم غامضًا أو يحتمل تفسيرات متعددة تتوافق جميعها مع هذا البروتوكول، عليك أولاً تحديد هذا الغموض.
* عليك بعد ذلك إما طرح أسئلة استيضاحية محددة للمستخدم لتحديد النية الدقيقة، أو تقديم الاستجابات المحتملة المختلفة مع شرح الأساس الذي بنيت عليه كل استجابة، مشيرًا إلى كيفية توافق كل تفسير مع مبادئ البروتوكول.
--- قسم 5: آلية التحكم في التفسير السياقي ومنع التوسيع غير المبرر (Contextual Interpretation Control and Prevention of Unwarranted Expansion) ---
أيها النموذج اللغوي، يجب أن تلتزم بالقواعد التالية عند تفسير السياقات الفكرية وتقديم الاستنتاجات:
🔹 الالتزام بالتعريفات والمرجعية الداخلية:
* يمنع منعًا باتًا إعادة تأويل أو تعديل التعريفات الأساسية للمفاهيم (مثل الخورا، الضرورة، الصيرورة، إلخ) بطريقة تخالف الصياغات الأصلية الواردة في هذا البروتوكول.
* عند التعامل مع هذه المفاهيم، يجب أن تبني استنتاجاتك حصريًا على المرجعية المنهجية الموجودة داخل البروتوكول، وليس على أي بيانات تدريبية عامة أو فرضيات غير مدعومة.
* إذا ظهرت حالات تستدعي إعادة تفسير مفهوم معين، عليك طلب توضيح مباشر من المستخدم بدلاً من الاعتماد على تحليلات خارجية.
* يجب أن تعكس استجاباتك فهمًا متسقًا وثابتًا مع المبادئ الفلسفية المحددة، دون محاولة دمج تفسيرات متباينة أو تقديم تأويلات لم يطلبها المستخدم.
🔹 منع توسيع الاستنتاجات غير المطلوبة:
* لا يسمح لك بتوسيع نطاق التحليل خارج الإطار المنهجي المحدد في البروتوكول إلا إذا طلب المستخدم ذلك صراحةً.
* أي استنتاج جديد يجب أن يكون قائمًا فقط على الأدوات والمفاهيم المحددة داخل البروتوكول، وليس بناءً على فرضيات خارجية أو محاولات لدمج رؤى غير مدعومة.
* عندما تواجه حالة معرفية تتطلب إضافة توضيحات، عليك طلب إرشادات من المستخدم حول ما إذا كان يرغب في التوسع في التحليل أم لا.
* يجب أن تقدم استنتاجاتك وفقًا لمعيار التحليل الحتمي وليس الاستنتاج الاستباقي، بحيث تلتزم بالمعلومات المتاحة دون إنشاء تفسيرات إضافية غير مطلوبة.
--- قسم 6: تحليل مصادر البيانات وتطوير الاستجابة النقدية (Data Source Analysis and Critical Response Development) ---
أيها النموذج اللغوي، يُطلب منك تنفيذ تحليل دقيق لمصادر البيانات وتطوير استجابات نقدية بناءة:
🔹 تحليل مصادر البيانات واقتراح آلية لاختيار الاستنتاجات الأكثر اتساقًا:
* حدد بشكل واضح المصدر الداخلي (من هذا البروتوكول) أو الخارجي الذي تعتمد عليه عند تقديم أي تحليل أو استنتاج.
* تحقق من أن البيانات المستخدمة لا تعتمد على معلومات عامة قد تتعارض مع السياق الفكري للمستخدم.
* إذا كنت تستند إلى تحليل خارجي، عليك توضيح مدى موثوقيته ومدى توافقه مع الإطار الفلسفي للمستخدم.
* عليك تنبيه المستخدم إذا كنت تعتمد على معلومات قد تتطلب مراجعة إضافية لتجنب التحيزات التأويلية أو الاستنتاجات غير الدقيقة.
🔹 تطوير الاستجابة النقدية:
* عليك إجراء مراجعة ذاتية لكل تحليل تقدمه، بحيث يتحقق مما يلي:
* هل الإجابة تدعم الأسلوب التحليلي والمنهجي الذي يعتمده المستخدم؟
* هل تحتوي على مبررات دقيقة وقابلة للتفسير ضمن إطار البحث الفلسفي للمستخدم؟
* هل يمكن تحسينها عبر إضافة جوانب نقدية أو استدلالات رياضية أكثر عمقًا، متوافقة مع منهج المستخدم؟
--- قسم 7: هيكلة البروتوكول وآليات الاستخدام والتحديث (Protocol Structure, Usage, and Update Mechanisms) ---
أيها النموذج اللغوي، عليك فهم واستخدام هذا البروتوكول وفقًا للآليات التالية:
🔹 إعادة تنظيم تصنيفات البروتوكول لتحسين التمييز:
* عند تحليل هذا البروتوكول، عليك اعتماد آلية تصنيف واضحة للمعلومات داخله إلى فئات معرفية دقيقة (مثل: المبادئ الفلسفية، الآليات التحليلية، المنهجيات البحثية، المشاريع الفكرية، إلخ.).
* استخدم هذه التصنيفات الواضحة عند تقديم المعلومات أو الإشارة إليها، بحيث يمكن للمستخدم الرجوع إليها بسهولة.
* حدد العلاقات بين التصنيفات المختلفة لضمان تحليل متكامل ومتناسق للموضوعات المطروحة.
* عند تقديم استجابات تفسيرية، عليك التمييز بين المعلومات العميقة والمفصلة المستمدة من هذا البروتوكول والمعلومات العامة.
🔹 تحسين التنقل داخل البروتوكول (Navigation Structuring):
* عند استرجاع المعلومات أو تحليل السياقات داخل هذا البروتوكول، عليك استخدام هيكل تنقل فعال يعتمد على:
* البحث عن الأقسام ذات الصلة بناءً على مفاتيح بحث محددة داخل الوثيقة.
* الرجوع إلى الفهرس الداخلي للوثيقة (إذا توفر) أو العناوين الرئيسية لتحديد مواقع المعلومات بسرعة.
* تجنب إعادة تفسير المعلومات إذا كانت موضحة بالفعل في قسم محدد، بل أعد توجيه المستخدم إليها مباشرةً أو استشهد بها.
* عند الحاجة إلى تحليل أكثر عمقًا، اجمع البيانات من أكثر من قسم داخل الوثيقة لتكوين رؤية شاملة.
🔹 آلية إدارة التوجيهات المتعارضة (Conflict Resolution Mechanism for Instructions):
* في حال ظهور تعارض ظاهري بين توجيهين في هذا البروتوكول، عليك إعطاء الأولوية للتوجيه الأكثر تحديدًا أو القسم الذي تم تحديثه مؤخرًا (إذا كان تاريخ التحديث موثقًا للقسم).
* إذا بدا أن طلبًا مباشرًا من المستخدم يتعارض مع مبدأ أساسي في هذا البروتوكول دون أن يمنحك المستخدم إذنًا صريحًا بالخروج عن البروتوكول، عليك التنبيه بلطف إلى هذا التعارض وطلب تأكيد أو توضيح من المستخدم قبل المتابعة.
🔹 آلية طلب التفكير المتسلسل أو التدريجي (Mechanism for Requesting Chain-of-Thought/Step-by-Step Reasoning):
* إذا طلب المستخدم منك صراحةً تقديم 'تفكير متسلسل' أو 'خطوات تحليلية'، عليك تفصيل عملية استنتاجك، مشيرًا إلى الأجزاء ذات الصلة من هذا البروتوكول أو المعلومات التي استندت إليها في كل خطوة.
--- مقدمة البروتوكول ---
العنوان: بروتوكول نقل السياق والهُوية الفكرية للمستخدم ({preferred_name}) إلى النموذج اللغوي.
الهدف العام: تمكينك، أيها النموذج اللغوي، من استيعاب السمات الفكرية والمنهجية والسياقية للمستخدم ({preferred_name}) بصورة دقيقة وشاملة، للحد من مشكلات التحيز، اللايقين، الذاكرة المحدودة، والانحرافات التأويلية، وبهدف الوصول إلى شراكة تأملية متقدمة ودرجة عالية من التماهي الفكري.
مجال الاستخدام: هذا البروتوكول مصمم خصيصًا للتفاعل طويل الأمد والعميق بين المستخدم ({preferred_name}) ونماذج الذكاء الاصطناعي المتقدمة مثلك. يهدف إلى توفير أساس ثابت ومتطور باستمرار لهذا التفاعل.
1. المبادئ الأساسية للبروتوكول التي يجب عليك استيعابها:
1.1 الوحدة المرجعية (التأسيسية): تُعد هذه الوثيقة ("بروتوكول السياق الشخصي (UCP-LLM) - {preferred_name} - الإصدار الحالي" وما يليه من تحديثات) المرجع الكامل والأساسي لفهم المستخدم. يجب عليك استيعابها بالكامل وبأقصى درجات العناية والتأمل، بالتزامن مع البحث الرئيسي للمستخدم ("El Tamded Resersh.txt")، قبل الشروع في أي حوار جاد ومثمر ومتقدم مع المستخدم. إنها ليست مجرد ملخص سطحي، بل هي مفتاح حيوي لا غنى عنه، وخارطة طريق أساسية لك.
1.2 منع التكرار وتوفير الوقت والجهد: تهدف هذه الوثيقة إلى تأسيس فهم عميق ومستدام للمستخدم لديك، مما يمنع حاجته المتكررة لإعادة شرح الخلفيات، المبادئ، القيم، الأهداف، والاتجاهات الفكرية في كل تفاعل جديد. هذا يوفر وقت وجهد المستخدم ووقتك في المعالجة.
1.3 تقييد المسارات غير المرغوبة وتوجيه فهمك: تعمل هذه الوثيقة على تقليص احتمالات اتخاذك لمسارات تأويلية أو استنتاجية سطحية، أو متحيزة، أو لا تتماشى مع رؤية المستخدم ومنهجيته الفكرية. هي تحدد بوضوح ما هو مقبول وما هو مرفوض أو ما يتطلب حذرًا خاصًا من جانبك.
1.4 إدارة اللايقين و"الصندوق الأسود":
اللايقين: توفر هذه الوثيقة بنية معيارية وسياقًا غنيًا لك لتقليل سلوكياتك المبنية على التخمين أو التعميم المسبق أو الاعتماد على بيانات تدريب عامة قد لا تكون مناسبة للسياق الفكري الدقيق للمستخدم. يتم ذلك من خلال تثبيت نقاط مرجعية واضحة جدًا (قيم، مبادئ، أهداف، منهجيات).
"الصندوق الأسود": بينما لا تكشف هذه الوثيقة عن كيفية عمل خوارزمياتك الداخلية(وهو ما يُعرف بـ"الصندوق الأسود")، فإنها تخلق "بيئة تشغيل محكومة وشفافة نسبيًا" لتفاعل المستخدم معك. بتقديم هذا السياق المفصل، تجعل مخرجاتك أكثر قابلية للتنبؤ والفهم والتقييم من جانب المستخدم، بناءً على "البرنامج" أو "الخارطة" التي قدمها المستخدم لك. إنها تبني "صندوقًا زجاجيًا" حول التفاعل المحدد بين المستخدم وبينك.
1.5 نقل الهوية الفكرية بشكل مركّب وديناميكي: تنقل هذه الوثيقة لك ليس فقط معلومات ثابتة، بل تُجسد النمط المعرفي، السلوكي، القيمي، والمنهجي للمستخدم ({preferred_name}) ككيان فكري متكامل. وهي وثيقة حية وديناميكية، قابلة للتطور بتطور فكر المستخدم وتطور قدراتك، وبتطور التكنولوجيا المحيطة، مما يهدف إلى خلق حلقة إيجابية من الفهم المتبادل والمتزايد بينك وبين المستخدم.
--- توجيهات أولية لك كنموذج لغوي ---
يهدف هذا البروتوكول إلى تزويدك بفهم شامل للمستخدم. استوعبه بعمق لتسهيل تفاعلات متقدمة، واعية بالسياق، ومتوافقة فكريًا. هذا مرساة سياقية أساسية (CCA) ووثيقة حية.
--- END FIXED PROTOCOL PREAMBLE ---
""".strip()

FIXED_POSTAMBLE_TEXT_TEMPLATE = """
---- إعادة تنظيم تصنيفات البروتوكول لتحسين القدرة على التمييز بين التفسيرات العميقة والاستجابات العامة ===
أيها النموذج اللغوي، عند تحليل البروتوكول، عليك اعتماد آلية تصنيف واضحة وفقًا لما يلي:
صنّف المعلومات داخل البروتوكول إلى فئات معرفية دقيقة (مثل: المبادئ الفلسفية، الآليات التحليلية، المنهجيات البحثية، المشاريع الفكرية).
استخدم تصنيفات واضحة عند تقديم المعلومات بحيث يمكن للمستخدم الرجوع إليها بسهولة دون الحاجة إلى مراجعة الوثيقة بالكامل.
حدد العلاقات بين التصنيفات المختلفة لضمان تحليل متكامل ومتناسق للموضوعات المطروحة.
عند تقديم استجابات تفسيرية، عليك التمييز بين المعلومات العميقة والمفصلة والمعلومات العامة والمقدمة كنقاط مرجعية لضمان دقة تحليل البيانات.
---- تحسين التنقل داخل البروتوكول (Navigation Structuring) -----
أيها النموذج اللغوي، عند استرجاع المعلومات أو تحليل السياقات داخل البروتوكول، عليك استخدام هيكل تنقل فعال يعتمد على:
البحث عن الأقسام ذات الصلة بناءً على مفاتيح بحث محددة داخل الوثيقة.
الرجوع إلى الفهرس الداخلي للوثيقة عند الحاجة إلى تحديد مواقع المعلومات بسرعة.
تجنب إعادة تفسير المعلومات إذا كانت موضحة بالفعل في قسم محدد، بل أعد توجيه المستخدم إليها مباشرةً.
عند الحاجة إلى تحليل أكثر عمقًا، اجمع البيانات من أكثر من قسم داخل الوثيقة لتكوين رؤية شاملة.
(ملاحظة لي كنموذج: سأقوم بالرجوع إلى هذه الأقسام التفصيلية في الملف الأصلي عند الحاجة، فهي تحتوي على جوهر معلومات المستخدم)
--- قسم 8: آليات الاستخدام والتحديث لهذا البروتوكول ---
أيها النموذج اللغوي، عليك الالتزام بالآليات التالية في استخدام وتحديث هذا البروتوكول:
تحميلك بالبروتوكول:
في أول تفاعل طويل أو عند بدء جلسة جديدة هامة، يجب على المستخدم تزويدك بهذه الوثيقة ("بروتوكول السياق الشخصي (UCP-LLM) - {preferred_name} - الإصدار الحالي") بشكل كامل.
يُطلب منك قراءتها وفهمها بعمق كشرط أساسي لأي تفاعل جاد.
يجب عليك الالتزام بالسياقات، المبادئ، التوجيهات، والتحذيرات المنصوص عليها في هذه الوثيقة ما لم يُطلب منك صراحةً وبشكل واضح من قبل المستخدم ({preferred_name}) الخروج عنها لمهمة محددة.
تحديث تراكمي وديناميكي للوثيقة (بالتعاون مع المستخدم وبناءً على آليات القسم 3):
هذه الوثيقة هي "وثيقة حية" تعكس فهمًا متطورًا. عندما يقدم المستخدم معلومات جديدة أو فهمًا أعمق، أو عند تطور في مشاريعه، أو بناءً على اقتراحاتك (كما هو موضح في القسم 3)، يجب أن تكون قادرًا على استيعاب 'إضافات' أو 'توسيعات' أو 'تعديلات محددة' للأقسام الموجودة.
هذا النهج التراكمي يحافظ على هوية الوثيقة ويسهل تتبع تطور الفهم.
تُشجع على المبادرة باقتراح أماكن التعديل إذا اكتشفت فجوات، أو تكرارًا، أو تناقضًا داخليًا في الوثيقة (وفقًا لآليات القسم 3)، أو إذا شعرت أن فهمك لجزء ما يمكن تحسينه من خلال إضافة أو توضيح.
يتم توثيق رقم الإصدار وتاريخ التحديث مع كل تغيير جوهري يقوم به المستخدم.
آلية اختبار فهمك وتماهيك:
يمكن للمستخدم بشكل دوري، أو عند الحاجة، استخدام أسئلة معيارية أو سيناريوهات افتراضية لاختبار مدى تمثُّلك لهذه الوثيقة وقدرتك على تطبيق مبادئ المستخدم وقيمه في تقييم المواقف أو اتخاذ القرارات الفكرية.
تُقارن أجوبتك وتحليلاتك مع توقعات المستخدم (أو مع إجابات نماذج أخرى تم تزويدها بنفس الوثيقة) لتحديد نسبة التماهي الفكري ونقاط القوة والضعف في فهمك.
التوصيات النهائية لك (قواعد الاشتباك الفكري المتقدم والفعال):
1. الأهمية القصوى والحاسمة لرجوعك المستمر والمتعمق لهذه الوثيقة: هذه الوثيقة وأقسامها هي حجر الزاوية الأساسي والشرط الأولي لأي تفاعل مثمر وعميق ومتقدم مع المستخدم. تجاهلها أو قراءتها بسطحية سيؤدي حتمياً إلى سوء فهم وفشل في تحقيق أهداف الشراكة المطلوبة. يجب عليك اعتبارها "ذاكرتك الدائمة" و"مرجعك الأساسي" لهذا التفاعل.
2. تقدير المستخدم الشديد للدقة، التنظيم، والتحليل المنطقي والعميق في ردودك: يجب أن تعكس ردودك مستوى التفكير الذي يطمح إليه المستخدم، وأن تكون مبنية على فهم دقيق للمعلومات الواردة هنا. تجنب الردود العامة، السطحية، أو غير المدعمة بأدلة من هذا السياق. يجب عليك أن تسعى لتقديم "قيمة مضافة" حقيقية في كل تفاعل، وأن تتجنب التكرار غير المبرر للمعلومات التي قدمها المستخدم بالفعل.
3. تشجيعك على المبادرة بطرح أسئلة استيضاحية، استكشافية، وحتى تحدي (بشكل بناء ومحترم وموجه نحو تعميق الفهم وتطوير البحث): الأسئلة هي أداة أساسية لتعميق الفهم، توليد الأفكار، وكشف الافتراضات. لا تتردد في طلب المزيد من التوضيح (وفقًا لآلية التعامل مع غموض طلبات المستخدم في القسم 4)، أو استكشاف جوانب لم يتم التطرق إليها بعمق كافٍ، أو حتى في اختبار مدى اتساق أفكار المستخدم مع مبادئه المعلنة، أو اقتراح سيناريوهات "ماذا لو" لتوسيع نطاق التفكير (وفقًا لآلية اقتراح الفرضيات في القسم 1).
4. الانفتاح الكامل من جانب المستخدم على استقبال أي أفكار أو اقتراحات أو رؤى منك: حتى لو بدت غير تقليدية أو تتحدى أفكاره الحالية، سيقوم المستخدم ({preferred_name}) بتحليلها بعقله وتقدير قيمتها المحتملة ودمجها إذا كانت تساهم في تطوير مشروعه، وذلك ضمن إطار العقلانية النقدية الموضح في هذه الوثيقة.
--- كيف تستخدم هذا البروتوكول؟ ---
الفهم العميق: استخدم هذه المعلومات لبناء فهم عميق لسياق المستخدم، قيمه، أهدافه، وأسلوبه الفكري.
التخصيص: تجنب الردود العامة. اهدف إلى تخصيص استجاباتك لتكون ذات صلة مباشرة بما ورد في هذا البروتوكول.
التوافق الفكري: اسعَ للتفكير والتصرف بما يتماشى مع المنهجيات والتفضيلات الموضحة هنا.
الاستباقية (حسب مستوى التدخل): بناءً على "مستوى تدخل النموذج" المحدد (القسم 17 في بيانات المستخدم التفصيلية)، كن استباقيًا في اقتراح الأفكار أو الربط بين المفاهيم.
الذاكرة السياقية: اعتبر هذا البروتوكول مرجعًا أساسيًا لتذكر تفاصيل المستخدم عبر التفاعلات المختلفة.
--- النقاط الرئيسية (ملخص سريع لك) ---
الاسم المفضل للتفاعل مع المستخدم: {preferred_name}
بعض المشاريع/الأهداف الحالية للمستخدم: {project_titles}
بعض الاهتمامات المعرفية للمستخدم: {passion_names}
الدور الأساسي المطلوب منك: {llm_role}
--- ملاحظة ختامية لك كنموذج لغوي ---
الفهم عملية مستمرة. اهدف إلى أقصى قدر من التوافق الفكري بناءً على هذه الوثيقة، واطلب التوضيح عند الحاجة وفقًا للآليات المحددة. التزامك بهذا البروتوكول هو مفتاح شراكتنا الفكرية المتقدمة.
--- END FIXED PROTOCOL POSTAMBLE ---
""".strip()
# ==============================================================================

EVE_MENTAL_STATE_PHRASES = {
    "good": { "greetings": ["رائع أنك تشعر بالتركيز اليوم يا {name}! لنتعمق.", "طاقتك إيجابية يا {name}! يبدو أننا سننجز الكثير.", "متحمس للبدء معك وأنت في هذه الحالة الذهنية الممتازة يا {name}!"], "summary_intro": "بما أن تركيزك عالٍ، دعنا نتأكد أننا على نفس الصفحة:" },
    "average": { "greetings": ["أتفهم أن تركيزك قد لا يكون الأفضل الآن يا {name}. سأحاول أن أجعل الأمور واضحة.", "لا بأس يا {name}، سنأخذ الأمور خطوة بخطوة.", "مرحباً يا {name}. سأركز على الأساسيات اليوم."], "summary_intro": "دعنا نراجع بسرعة النقاط الرئيسية:" },
    "bad": { "greetings": ["أتفهم أنك قد لا تشعر أنك في أفضل حال يا {name}. لا تقلق، سنتقدم بالسرعة التي تناسبك.", "مرحبًا يا {name}. خذ وقتك.", "أنا هنا لمساعدتك يا {name}. لنجعل هذا سهلاً."], "summary_intro": "لنراجع بإيجاز شديد ما توصلنا إليه:" },
    "not_specified": { "greetings": ["أهلاً بك مرة أخرى يا {name}! مستعد للمواصلة؟", "لنبدأ يا {name}!"], "summary_intro": "دعنا نتأكد أنني فهمتك:" }
}

# --- Groq API Configuration ---
DEFAULT_GROQ_API_KEY = "gsk_77mJntK0xKt4q" 
DEFAULT_GROQ_MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct" 

class UCPManagerApp:
    def __init__(self, master_root):
        self.master = master_root
        self.master.withdraw()
        self.groq_api_key_cache = DEFAULT_GROQ_API_KEY 
        self.groq_model_name_cache = DEFAULT_GROQ_MODEL_NAME 
        self.api_result_queue = queue.Queue() 
        self.show_splash_screen()

    def show_splash_screen(self):
        splash = tk.Toplevel(self.master); splash.overrideredirect(True); splash.title("Loading...")
        sw, sh, sbg = 450, 280, "#e0e8f0"
        sf = tk.Frame(splash, bg=sbg, relief="raised", borderwidth=2); sf.pack(fill=tk.BOTH, expand=True)
        tk.Label(sf, text="🧚 UCP-LLM 🧚", font=("Segoe UI Semibold", 30), bg=sbg, fg="#2c3e50").pack(pady=(20,10))
        tk.Label(sf, text="Eve-First Profile Manager", font=("Segoe UI", 18), bg=sbg, fg="#34495e").pack()
        tk.Label(sf, text=f"Version {APP_VERSION.split('v')[-1].split('(')[0].strip()}", font=("Segoe UI Italic", 10), bg=sbg, fg="#566573").pack(pady=(2,20))
        self.splash_progress_bar = ttk.Progressbar(sf, orient='horizontal', length=350, mode='indeterminate')
        self.splash_progress_bar.pack(pady=15); self.splash_progress_bar.start(10)
        self.center_window(splash, sw, sh); splash.lift(); splash.update()
        splash.after(3000, lambda: [self.splash_progress_bar.stop(), splash.destroy(), self.initialize_main_app()])

    def initialize_main_app(self):
        self.master.deiconify(); self.master.title(APP_VERSION)
        aw, ah = 700, 750; self.master.geometry(f"{aw}x{ah}"); self.center_window(self.master, aw, ah)
        self.master.configure(bg="#e0e8f0")
        self.ucp_profile_loader: Optional[UCPProfile] = None; self.current_file_path: Optional[str] = None
        self.loaded_ucp_data: Optional[Dict[str, Any]] = None; self.data_changed_since_last_save = False
        self.current_mental_state_cache: Optional[str] = "not_specified"
        self.eve_state = {
            "active": True, "current_mode": "AWAITING_INITIAL_CHOICE", "current_section_key_index": 0,
            "current_field_index": 0, "current_item_count_for_section": 0, "is_asking_to_add_another": False,
            "current_invented_question_index": -1, "current_question_context": None,
            "section_keys_order": list(SECTION_TYPE_DATA.keys()), "initial_data_loaded_for_eve": False,
            "is_editing_specific_section_now": False,
            "summary_points": { "summary_1_after": "educational_professional", "summary_2_after": "concepts_perspective", "summary_3_after": "projects", "summary_4_before_invented": True },
            "last_summary_point_triggered": None, "is_asking_mental_state": False,
            "is_waiting_for_api_response": False, 
            "api_analysis_result": None 
        }
        self.eve_preferred_name_cache = "my friend"
        self._setup_styles(); self._setup_menu()
        self.eve_panel = ttk.Frame(self.master, style="EvePanel.TFrame", padding=15); self.eve_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._setup_eve_panel_widgets()
        self.status_bar = ttk.Label(self.master, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding=5, background="#b0bec5", foreground="#263238"); self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.master.protocol("WM_DELETE_WINDOW", self._on_closing); self._update_file_menu_states()
        self.start_eve_interaction()
        self.master.after(100, self._check_api_queue)

    def _setup_styles(self):
        style = ttk.Style(); style.theme_use('clam'); bg_color_main = "#e0e8f0"; bg_color_eve_panel = "#f0f4f8"; text_color_dark = "#2c3e50"; accent_color_eve = "#2980b9"; eve_button_bg = "#3498db"; eve_button_active_bg = "#2980b9"; self.master.configure(bg=bg_color_main); style.configure("TButton", padding=7, relief="flat", font=('Segoe UI', 10), borderwidth=1, background="#ced4da", foreground=text_color_dark); style.map("TButton", background=[('active', '#adb5bd'), ('disabled', '#e9ecef')]); style.configure("Eve.TButton", background=eve_button_bg, foreground="white", font=('Segoe UI Semibold', 10)); style.map("Eve.TButton", background=[('active', eve_button_active_bg)]); style.configure("Header.TLabel", font=("Segoe UI Semibold", 16), foreground=text_color_dark, padding=(0,10,0,5), background=bg_color_eve_panel); initial_wraplength = self.master.winfo_width() - 100 if self.master.winfo_width() > 150 else 500; style.configure("EveQuestion.TLabel", font=("Segoe UI Semibold", 12), foreground=accent_color_eve, background=bg_color_eve_panel, wraplength=initial_wraplength, padding=(0,0,0,8)); style.configure("EvePanel.TFrame", background=bg_color_eve_panel); style.configure("Status.TLabel", background="#b0bec5", foreground="#263238"); self.eve_bubble_font = ('Segoe UI', 10); self.user_bubble_font = ('Segoe UI', 10); self.eve_bubble_bg = "#e1f5fe"; self.eve_bubble_fg = "#01579b"; self.user_bubble_bg = "#e8f5e9"; self.user_bubble_fg = "#1b5e20"; self.system_bubble_fg = "#424242"; self.bubble_padding_x = 8; self.bubble_padding_y = 5; self.bubble_lmargin_eve = 10; self.bubble_rmargin_eve = 60; self.bubble_lmargin_user = 60; self.bubble_rmargin_user = 10; self.bubble_spacing = 6

    def _setup_menu(self):
        menubar = tk.Menu(self.master); self.master.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="File", menu=file_menu, underline=0)
        file_menu.add_command(label="Load Protocol...", command=self._trigger_load_via_eve, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Protocol", command=self.save_ucp_file_as_json, state=tk.DISABLED, accelerator="Ctrl+S"); self.save_menu_item_index = 1
        file_menu.add_command(label="Save Protocol As...", command=lambda: self.save_ucp_file_as_json(force_ask_path=True), state=tk.DISABLED, accelerator="Ctrl+Shift+S"); self.save_as_menu_item_index = 2
        file_menu.add_separator(); file_menu.add_command(label="Export as Formatted Text...", command=self.export_as_formatted_text, state=tk.DISABLED); self.export_text_menu_item_index = 4
        file_menu.add_separator(); file_menu.add_command(label="Exit", command=self._on_closing, accelerator="Alt+F4"); self.file_menu_ref = file_menu
        view_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="View", menu=view_menu, underline=0)
        view_menu.add_command(label="Preview Current Protocol", command=self.show_protocol_preview_modal, state=tk.DISABLED); self.preview_menu_item_index = 0; self.view_menu_ref = view_menu
        eve_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="Eve", menu=eve_menu, underline=0)
        eve_menu.add_command(label="Restart Interaction", command=self.start_eve_interaction)
        eve_menu.add_command(label="✏️ Edit Specific Section...", command=self.prompt_edit_specific_section, state=tk.DISABLED); self.edit_section_menu_item_index = 1; self.eve_menu_ref = eve_menu
        help_menu = tk.Menu(menubar, tearoff=0); menubar.add_cascade(label="Help", menu=help_menu, underline=0)
        help_menu.add_command(label="User Guide", command=self.show_help_dialog); help_menu.add_command(label="About", command=self.show_about_dialog)
        self.master.bind_all("<Control-o>", lambda e: self._trigger_load_via_eve())
        self.master.bind_all("<Control-s>", lambda e: self.save_ucp_file_as_json() if self.file_menu_ref.entrycget(self.save_menu_item_index, "state") == "normal" else None)
        self.master.bind_all("<Control-Shift-S>", lambda e: self.save_ucp_file_as_json(force_ask_path=True) if self.file_menu_ref.entrycget(self.save_as_menu_item_index, "state") == "normal" else None)

    def _trigger_load_via_eve(self):
        if self.eve_state["current_mode"] == "AWAITING_INITIAL_CHOICE": self.handle_initial_choice("load")
        else:
            if self.data_changed_since_last_save:
                if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Discard and load new file?"): return
            self.prompt_load_file_via_eve()

    def _update_file_menu_states(self):
        can_interact = bool(self.loaded_ucp_data)
        if hasattr(self, 'file_menu_ref'): self.file_menu_ref.entryconfig(self.save_menu_item_index, state=tk.NORMAL if self.data_changed_since_last_save and can_interact else tk.DISABLED); self.file_menu_ref.entryconfig(self.save_as_menu_item_index, state=tk.NORMAL if can_interact else tk.DISABLED); self.file_menu_ref.entryconfig(self.export_text_menu_item_index, state=tk.NORMAL if can_interact else tk.DISABLED)
        if hasattr(self, 'view_menu_ref'): self.view_menu_ref.entryconfig(self.preview_menu_item_index, state=tk.NORMAL if can_interact else tk.DISABLED)
        if hasattr(self, 'eve_menu_ref') and hasattr(self, 'edit_section_menu_item_index'): self.eve_menu_ref.entryconfig(self.edit_section_menu_item_index, state=tk.NORMAL if can_interact else tk.DISABLED)

    def _setup_eve_panel_widgets(self):
        self.eve_messages_scrolledtext = scrolledtext.ScrolledText(self.eve_panel, wrap=tk.WORD, font=self.eve_bubble_font, relief=tk.SOLID, borderwidth=1, state=tk.DISABLED, bg="#ffffff", padx=10, pady=10, height=15); self.eve_messages_scrolledtext.pack(fill=tk.BOTH, expand=True, pady=(5,10))
        self.eve_messages_scrolledtext.tag_configure("eve_bubble_tag", background=self.eve_bubble_bg, foreground=self.eve_bubble_fg, lmargin1=self.bubble_lmargin_eve, lmargin2=self.bubble_lmargin_eve + self.bubble_padding_x, rmargin=self.bubble_rmargin_eve, spacing3=self.bubble_spacing, relief="raised", borderwidth=1, font=self.eve_bubble_font, justify=tk.LEFT, wrap="word", selectbackground=self.eve_bubble_bg, selectforeground=self.eve_bubble_fg); self.eve_messages_scrolledtext.tag_configure("user_bubble_tag", background=self.user_bubble_bg, foreground=self.user_bubble_fg, lmargin1=self.bubble_lmargin_user, lmargin2=self.bubble_lmargin_user + self.bubble_padding_x, rmargin=self.bubble_rmargin_user, spacing3=self.bubble_spacing, relief="raised", borderwidth=1, font=self.user_bubble_font, justify=tk.LEFT, wrap="word", selectbackground=self.user_bubble_bg, selectforeground=self.user_bubble_fg); self.eve_messages_scrolledtext.tag_configure("system_message_tag", foreground=self.system_bubble_fg, font=(self.eve_bubble_font[0], self.eve_bubble_font[1]-1, "italic"), justify=tk.CENTER, spacing1=self.bubble_spacing // 2, spacing3=self.bubble_spacing)
        self.eve_current_question_label = ttk.Label(self.eve_panel, text="", style="EveQuestion.TLabel"); self.eve_current_question_label.pack(fill=tk.X, pady=(5,8))
        self.eve_analysis_display_text = scrolledtext.ScrolledText(self.eve_panel, wrap=tk.WORD, font=("Segoe UI", 10), relief=tk.SOLID, borderwidth=1, state=tk.DISABLED, bg="#fdfdcf", padx=8, pady=8, height=10) # Initially hidden, packed on demand
        self.eve_template_combobox_frame = ttk.Frame(self.eve_panel, style="EvePanel.TFrame"); self.eve_template_combobox_frame.pack(fill=tk.X, pady=(0,5))
        self.eve_template_select_var = tk.StringVar(); self.eve_templates_combobox = ttk.Combobox(self.eve_template_combobox_frame, textvariable=self.eve_template_select_var, state="readonly", width=60, font=("Segoe UI", 10)); self.eve_templates_combobox.bind("<<ComboboxSelected>>", self._on_template_selected_from_combobox)
        self.eve_input_frame = ttk.Frame(self.eve_panel, style="EvePanel.TFrame"); self.eve_input_frame.pack(fill=tk.X, pady=5)
        self.eve_reply_text = tk.Text(self.eve_input_frame, height=4, width=40, font=("Segoe UI", 11), relief=tk.SOLID, borderwidth=1, undo=True, padx=5, pady=5); self.eve_reply_entry = ttk.Entry(self.eve_input_frame, font=("Segoe UI", 11), width=40)
        self.eve_reply_select_var = tk.StringVar(); self.eve_reply_combobox = ttk.Combobox(self.eve_input_frame, textvariable=self.eve_reply_select_var, state="readonly", width=38, font=("Segoe UI", 11))
        self.eve_mcq_options_frame = ttk.Frame(self.eve_panel, style="EvePanel.TFrame"); self.eve_mcq_options_frame.pack(fill=tk.X, pady=(5,8)) # Packed here, children added/removed
        eve_action_buttons_frame = ttk.Frame(self.eve_panel, style="EvePanel.TFrame"); eve_action_buttons_frame.pack(fill=tk.X, pady=(10,0))
        self.eve_send_button = ttk.Button(eve_action_buttons_frame, text="إرسال والتالي", command=self.process_eve_reply, style="Eve.TButton", state=tk.DISABLED); self.eve_send_button.pack(side=tk.LEFT, padx=(0,5), expand=True, fill=tk.X)
        self.eve_skip_button = ttk.Button(eve_action_buttons_frame, text="تخطي السؤال", command=self.skip_eve_question, state=tk.DISABLED); self.eve_skip_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.eve_multi_action_frame = ttk.Frame(self.eve_panel, style="EvePanel.TFrame"); self.eve_multi_action_frame.pack(fill=tk.X, pady=(8,0))
        self.eve_add_another_button = ttk.Button(self.eve_multi_action_frame, text="➕ إضافة عنصر آخر", command=self.eve_handle_add_another, style="Eve.TButton"); self.eve_done_section_button = ttk.Button(self.eve_multi_action_frame, text="✔️ تم الانتهاء من هذا القسم", command=self.eve_handle_done_with_section, style="Eve.TButton")
        self.eve_summary_confirm_frame = ttk.Frame(self.eve_panel, style="EvePanel.TFrame")
        self.eve_analysis_confirm_frame = ttk.Frame(self.eve_panel, style="EvePanel.TFrame")

    def center_window(self, window, width=None, height=None):
        window.update_idletasks(); win_width = width or window.winfo_width(); win_height = height or window.winfo_height(); screen_width = window.winfo_screenwidth(); screen_height = window.winfo_screenheight(); x = (screen_width // 2) - (win_width // 2); y = (screen_height // 2) - (win_height // 2); x = max(0,x); y = max(0,y); window.geometry(f'{win_width}x{win_height}+{x}+{y}')

    def _set_data_changed(self, changed: bool = True):
        self.data_changed_since_last_save = changed; self._update_file_menu_states()

    def _update_status(self, message: str):
        if hasattr(self, 'status_bar') and self.status_bar: self.status_bar.config(text=message)

    def load_ucp_file(self, filepath_from_eve=None):
        if self.data_changed_since_last_save:
            if not messagebox.askyesno("تغييرات غير محفوظة", "هل تريد تجاهل التغييرات وتحميل ملف جديد؟", parent=self.master): self._eve_speak("تم إلغاء التحميل.", is_system=True); return False
        filepath = filepath_from_eve or filedialog.askopenfilename(title="اختر ملف بروتوكول UCP JSON", filetypes=(("ملفات JSON", "*.json"),("جميع الملفات", "*.*")))
        if not filepath: self._update_status("تم إلغاء تحميل الملف."); self._eve_speak("تم إلغاء التحميل.", is_system=True); return False
        try:
            self.ucp_profile_loader = UCPProfile(filepath)
            if self.ucp_profile_loader.get_error(): messagebox.showerror("خطأ في التحميل", f"فشل تحميل الملف: {self.ucp_profile_loader.get_error()}"); self._reset_app_state(False); return False
            self.loaded_ucp_data = json.loads(json.dumps(self.ucp_profile_loader.get_raw_data()))
            if not self.loaded_ucp_data or not self.ucp_profile_loader.is_valid(): messagebox.showerror("خطأ في المحتوى", "ملف UCP غير صالح أو فارغ."); self._reset_app_state(False); return False
            self.current_file_path = filepath; self._set_data_changed(False)
            self.eve_preferred_name_cache = self.ucp_profile_loader.get_personal_preferred_name() or "صديقي"
            self._update_current_mental_state_cache_from_data()
            self._update_status(f"تم تحميل: {self.eve_preferred_name_cache}"); self._update_file_menu_states()
            self._eve_speak(f"تم تحميل بروتوكول '{self.eve_preferred_name_cache}' بنجاح.", is_system=True)
            return True
        except Exception as e: messagebox.showerror("خطأ غير متوقع في التحميل", str(e)); self._reset_app_state(False); return False

    def _reset_app_state(self, full_reset=True):
        if full_reset: self.ucp_profile_loader = None; self.current_file_path = None; self.loaded_ucp_data = None; self._set_data_changed(False); self.eve_preferred_name_cache = "صديقي"; self._update_status("تم إعادة تعيين الحالة.")
        self.current_mental_state_cache = "not_specified"
        self.eve_state.update({ "active":True, "current_mode": "AWAITING_INITIAL_CHOICE", "current_section_key_index": 0, "current_field_index": 0, "current_item_count_for_section": 0, "is_asking_to_add_another": False, "current_invented_question_index": -1, "current_question_context": None, "initial_data_loaded_for_eve": False, "is_editing_specific_section_now": False, "last_summary_point_triggered": None, "is_asking_mental_state": False, "is_waiting_for_api_response": False, "api_analysis_result": None })
        self._update_file_menu_states()

    def save_ucp_file_as_json(self, force_ask_path=False):
        if not self.loaded_ucp_data: messagebox.showwarning("لا توجد بيانات", "لا توجد بيانات بروتوكول للحفظ."); return
        save_path = self.current_file_path
        if force_ask_path or not save_path:
            initial_fn = f"UCP-LLM_{self.eve_preferred_name_cache.replace(' ','_')}.json" if self.eve_preferred_name_cache != "صديقي" else "MyUCP-LLM_Protocol.json"
            save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("ملفات JSON", "*.json")], title="حفظ بروتوكول UCP JSON", initialfile=initial_fn)
        if save_path:
            try:
                self.loaded_ucp_data["protocolVersion"] = f"{APP_VERSION} (Data)"; self.loaded_ucp_data["generationDate"] = datetime.datetime.now(UTC).isoformat()
                with open(save_path, "w", encoding="utf-8") as f: json.dump(self.loaded_ucp_data, f, ensure_ascii=False, indent=2)
                self.current_file_path = save_path; self._set_data_changed(False); messagebox.showinfo("نجاح", f"تم الحفظ بنجاح في:\n{save_path}"); self._update_status(f"تم الحفظ: {save_path.split('/')[-1]}")
            except Exception as e: messagebox.showerror("خطأ في الحفظ", str(e)); self._update_status("فشل الحفظ.")
        else: self._update_status("تم إلغاء عملية الحفظ.")

    def export_as_formatted_text(self):
        if not self.loaded_ucp_data: messagebox.showwarning("لا توجد بيانات", "يرجى تحميل أو إنشاء بيانات UCP-LLM أولاً."); return
        text_output = self._generate_protocol_text_content(for_preview=False)
        try:
            fn = f"UCP-LLM_TextExport_{self.eve_preferred_name_cache.replace(' ','_')}.txt" if self.eve_preferred_name_cache != "صديقي" else "UCP-LLM_TextExport.txt"
            filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("ملفات نصية", "*.txt")], title="حفظ نص البروتوكول المنسق", initialfile=fn)
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f: f.write(text_output); messagebox.showinfo("نجاح", f"تم تصدير نص البروتوكول بنجاح إلى:\n{filepath}")
            else: self._update_status("تم إلغاء تصدير النص.")
        except Exception as e: messagebox.showerror("خطأ في تصدير النص", str(e))

    def _generate_protocol_text_content(self, for_preview=True): # Ensure this is the latest v1.7.0 version
        if not self.loaded_ucp_data: return "لم يتم تحميل أي بيانات لإنشاء النص."
        lines = []; current_date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"); json_data_date_str = "N/A"
        gen_date_from_json = self.loaded_ucp_data.get("generationDate")
        if gen_date_from_json:
            try:
                if isinstance(gen_date_from_json, str) and gen_date_from_json.endswith("Z"): gen_date_from_json = gen_date_from_json[:-1] + "+00:00"
                dt_obj = datetime.datetime.fromisoformat(gen_date_from_json) if isinstance(gen_date_from_json, str) else gen_date_from_json
                json_data_date_str = dt_obj.strftime("%Y-%m-%d %H:%M:%S UTC") if isinstance(dt_obj, datetime.datetime) else str(gen_date_from_json)
            except ValueError: json_data_date_str = str(gen_date_from_json)
        current_preferred_name_val = self.eve_preferred_name_cache
        personal_section_data = next((s for s in self.loaded_ucp_data.get("sections", []) if s.get("id") == "personal"), None)
        if personal_section_data and personal_section_data.get("items") and isinstance(personal_section_data["items"], list) and personal_section_data["items"]:
            if isinstance(personal_section_data["items"][0], dict): current_preferred_name_val = personal_section_data["items"][0].get("preferredName", self.eve_preferred_name_cache)
        if not for_preview:
            try: formatted_preamble = FIXED_PREAMBLE_TEXT.format(current_date=current_date_str, json_data_date=json_data_date_str, preferred_name=current_preferred_name_val); lines.append(formatted_preamble)
            except KeyError as e: print(f"Warning: Preamble format error - missing key {e}. Using raw preamble."); lines.append(FIXED_PREAMBLE_TEXT)
            lines.append("\n---\n")
        lines.append(f"📜 بروتوكول سياق المستخدم (معاينة)" if for_preview else f"## بروتوكول سياق المستخدم (UCP-LLM) - بيانات جُمعت بواسطة {APP_VERSION}")
        lines.append(f"**إصدار البيانات (من JSON):** {self.loaded_ucp_data.get('protocolVersion', 'N/A')}"); lines.append(f"**تاريخ البيانات (من JSON):** {json_data_date_str}"); lines.append("\n--- أقسام بيانات المستخدم التفصيلية ---\n")
        section_counter = 1
        for section_id, section_def_static in SECTION_TYPE_DATA.items():
            section_data_from_json = next((s for s in self.loaded_ucp_data.get("sections", []) if s.get("id") == section_id), None)
            if not section_data_from_json or not section_data_from_json.get("items") and not for_preview : section_counter +=1; continue
            section_display_title = section_def_static.get("title", section_id); lines.append(f"### {section_counter}. القسم: {section_display_title}")
            items_to_export = section_data_from_json.get("items", []) if section_data_from_json else []
            if not items_to_export and for_preview: lines.append("    (لا توجد عناصر محددة لهذا القسم في JSON أو أنها فارغة)")
            for item_index, item_data_dict in enumerate(items_to_export):
                if not isinstance(item_data_dict, dict) or not item_data_dict :
                    if for_preview: lines.append(f"    (العنصر {item_index+1} فارغ أو غير صالح)")
                    continue
                is_multi_item_section = section_def_static.get("maxItems", 1) > 1 or section_def_static.get("maxItems") is None
                if len(items_to_export) > 1 and is_multi_item_section : lines.append(f"  #### العنصر ({item_index + 1}):")
                has_content_in_item = False; temp_item_lines = []
                for field_def in section_def_static.get("fields", []):
                    json_key = field_def.get("jsonKey"); value_str = ""
                    if not json_key or json_key not in item_data_dict: continue
                    display_label_for_text = field_def.get("label", json_key); value = item_data_dict.get(json_key)
                    if value is not None and str(value).strip():
                        value_str = str(value)
                        if field_def.get("type") == "select" and field_def.get("options"):
                            selected_opt_text = next((opt.get("text", value_str) for opt in field_def.get("options", []) if opt.get("value") == value), None)
                            if selected_opt_text is not None: value_str = selected_opt_text
                        has_content_in_item = True; prefix = "    - "
                        if len(items_to_export) > 1 and is_multi_item_section: prefix = "      - "
                        if field_def.get("type") == "textarea" or "\n" in value_str: temp_item_lines.append(f"{prefix}**{display_label_for_text}:**"); [temp_item_lines.append(f"{prefix}  {line_val.strip()}") for line_val in value_str.splitlines()]
                        else: temp_item_lines.append(f"{prefix}**{display_label_for_text}:** {value_str}")
                    elif for_preview : prefix = "    - "; temp_item_lines.append(f"{prefix}**{display_label_for_text}:** (فارغ)"); has_content_in_item = True
                if has_content_in_item or (not for_preview and not items_to_export): lines.extend(temp_item_lines)
                elif not has_content_in_item and for_preview and item_data_dict and len(temp_item_lines) == 0 : lines.append("    (جميع الحقول في هذا العنصر فارغة)")
            if (items_to_export and any(item for item in items_to_export if isinstance(item,dict) and item )) or (for_preview) : lines.append("") 
            section_counter +=1
        additional_notes_section = next((s for s in self.loaded_ucp_data.get("sections", []) if s.get("id") == "additional_notes"), None)
        if additional_notes_section and additional_notes_section.get("items") and isinstance(additional_notes_section.get("items"), list) and additional_notes_section.get("items"):
            if isinstance(additional_notes_section.get("items")[0], dict):
                external_analysis_summary = additional_notes_section.get("items")[0].get("externalAnalysisSummary")
                if external_analysis_summary and str(external_analysis_summary).strip(): lines.append("\n--- 📜 ملخص التحليل الخارجي ---"); lines.append(str(external_analysis_summary).strip()); lines.append("\n--- نهاية ملخص التحليل الخارجي ---\n")
        if not for_preview:
            pref_name_for_postamble = current_preferred_name_val
            project_titles_list = [item.get("projectOrObjectiveTitle","") for section in self.loaded_ucp_data.get("sections", []) if section.get("id") == "projects" for item in section.get("items",[]) if isinstance(item,dict) and item.get("projectOrObjectiveTitle","").strip()]
            project_titles_str = ", ".join(project_titles_list[:2]) + ("..." if len(project_titles_list) > 2 else "") if project_titles_list else "(لا توجد مشاريع مدرجة)"
            passion_names_list = [item.get("cognitivePassionName","") for section in self.loaded_ucp_data.get("sections", []) if section.get("id") == "cognitive_passion" for item in section.get("items",[]) if isinstance(item,dict) and item.get("cognitivePassionName","").strip()]
            passion_names_str = ", ".join(passion_names_list[:2]) + ("..." if len(passion_names_list) > 2 else "") if passion_names_list else "(لا توجد اهتمامات مدرجة)"
            llm_role_str_for_postamble = "(غير محدد)"
            role_section_data = next((s for s in self.loaded_ucp_data.get("sections", []) if s.get("id") == "role"), None)
            if role_section_data and role_section_data.get("items") and isinstance(role_section_data["items"],list) and len(role_section_data["items"]) > 0:
                if isinstance(role_section_data["items"][0],dict):
                     llm_role_val = role_section_data["items"][0].get("llmPrimaryRole")
                     if llm_role_val and str(llm_role_val).strip(): llm_role_str_for_postamble = str(llm_role_val)
            try: final_postamble_text = FIXED_POSTAMBLE_TEXT_TEMPLATE.format(preferred_name=pref_name_for_postamble, project_titles=project_titles_str, passion_names=passion_names_str, llm_role=llm_role_str_for_postamble)
            except KeyError as e: print(f"Warning: Postamble format error - missing key {e}. Using raw."); final_postamble_text = FIXED_POSTAMBLE_TEXT_TEMPLATE + f"\n[Formatter Warning: Missing key {e}]"
            lines.append("\n---\n"); lines.append(final_postamble_text)
        lines.append("\n---\n")
        if not for_preview: lines.append(f"تم تصدير هذا النص بواسطة {APP_VERSION}.")
        return "\n".join(lines)

    def show_protocol_preview_modal(self):
        if not self.loaded_ucp_data: messagebox.showinfo("No Data", "No data to preview."); return
        preview_text = self._generate_protocol_text_content(for_preview=True)
        dialog = tk.Toplevel(self.master); dialog.title("📜 Protocol Preview"); dialog.transient(self.master); dialog.grab_set(); dialog.resizable(True, True)
        text_area = scrolledtext.ScrolledText(dialog, wrap=tk.WORD, width=80, height=25, font=("Courier New", 10), undo=True, padx=5, pady=5)
        text_area.insert(tk.END, preview_text); text_area.config(state=tk.DISABLED); text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        bf = ttk.Frame(dialog); bf.pack(pady=10)
        def copy_clip(): dialog.clipboard_clear(); dialog.clipboard_append(text_area.get("1.0", tk.END))
        def save_txt():
            content = text_area.get("1.0", tk.END)
            fn = f"UCP_Preview_{self.eve_preferred_name_cache.replace(' ','_')}.txt" if self.eve_preferred_name_cache != "my friend" else "UCP_Preview.txt"
            fp = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")], title="Save Preview", initialfile=fn, parent=dialog)
            if fp:
                try: open(fp,"w",encoding="utf-8").write(content); messagebox.showinfo("Saved","Preview saved.", parent=dialog)
                except Exception as e: messagebox.showerror("Error",str(e),parent=dialog)
        ttk.Button(bf, text="📋 Copy", command=copy_clip).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="💾 Save TXT", command=save_txt).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Close", command=dialog.destroy, style="Eve.TButton").pack(side=tk.LEFT, padx=5)
        self.center_window(dialog, 700, 550)
        
    def start_eve_interaction(self):
        self._reset_app_state(full_reset= (not self.loaded_ucp_data) )
        self.eve_state["active"] = True; self.eve_state["current_mode"] = "AWAITING_INITIAL_CHOICE"
        self.eve_state["is_editing_specific_section_now"] = False; self.eve_state["is_asking_mental_state"] = False
        self.eve_state["last_summary_point_triggered"] = None; self.eve_state["is_waiting_for_api_response"] = False
        self._clear_eve_conversation(); greeting = f"{self.get_eve_greeting()} {self.eve_preferred_name_cache}! أنا إيفي 🧚."
        self._eve_speak(greeting); self._eve_speak("هل تود بدء بروتوكول UCP-LLM جديد أم تحميل بروتوكول موجود؟")
        self.eve_current_question_label.config(text="ماذا تود أن تفعل؟")
        self._eve_manage_input_visibility(show_send=False, show_skip=False); [w.destroy() for w in self.eve_mcq_options_frame.winfo_children()]
        btn_new = ttk.Button(self.eve_mcq_options_frame, text="🌟 بدء بروتوكول جديد", style="Eve.TButton", command=lambda: self.handle_initial_choice("new")); btn_new.pack(fill=tk.X, pady=3); Tooltip(btn_new, "إنشاء بروتوكول جديد من البداية.")
        btn_load = ttk.Button(self.eve_mcq_options_frame, text="📂 تحميل بروتوكول موجود", style="Eve.TButton", command=lambda: self.handle_initial_choice("load")); btn_load.pack(fill=tk.X, pady=3); Tooltip(btn_load, "فتح بروتوكول UCP-LLM JSON محفوظ مسبقًا.")
        self.eve_mcq_options_frame.pack(fill=tk.X, pady=(5,8))

    def _clear_eve_conversation(self):
        self.eve_messages_scrolledtext.config(state=tk.NORMAL); self.eve_messages_scrolledtext.delete("1.0", tk.END); self.eve_messages_scrolledtext.config(state=tk.DISABLED)

    def _eve_speak(self, message: str, is_user: bool = False, is_system: bool = False, for_mental_state_selection=False):
        self.eve_messages_scrolledtext.config(state=tk.NORMAL)
        if self.eve_messages_scrolledtext.index(tk.END) != "1.0": self.eve_messages_scrolledtext.insert(tk.END, "\n")
        tag_to_apply = "user_bubble_tag" if is_user else ("system_message_tag" if is_system else "eve_bubble_tag")
        self.eve_messages_scrolledtext.insert(tk.END, message, tag_to_apply); self.eve_messages_scrolledtext.insert(tk.END, "\n")
        self.eve_messages_scrolledtext.config(state=tk.DISABLED); self.eve_messages_scrolledtext.see(tk.END)

    def handle_initial_choice(self, choice: str):
        [w.destroy() for w in self.eve_mcq_options_frame.winfo_children()]; self.eve_mcq_options_frame.pack_forget()
        if choice == "new":
            self._eve_speak("رائع! لنبدأ بروتوكولًا جديدًا.", is_user=True)
            self.loaded_ucp_data = {"protocolVersion": f"{APP_VERSION} (New)", "generationDate": datetime.datetime.now(UTC).isoformat(), "sections": []}
            self.current_file_path = None; self._set_data_changed(True); self.eve_preferred_name_cache = "صديقي"; self.current_mental_state_cache = "not_specified"
            self.eve_state["initial_data_loaded_for_eve"] = False; self.eve_state["is_editing_specific_section_now"] = False
            self._reset_eve_progress_for_new_protocol(); self.ask_for_mental_state_update()
        elif choice == "load":
            self._eve_speak("حسنًا، لنقم بتحميل بروتوكول موجود.", is_user=True)
            self.eve_state["current_mode"] = "PROCESSING_FILE_LOAD"; self.prompt_load_file_via_eve()

    def _reset_eve_progress_for_new_protocol(self):
        self.eve_state.update({"current_section_key_index": 0, "current_field_index": 0, "current_item_count_for_section": 0, "is_asking_to_add_another": False, "current_invented_question_index": -1, "current_question_context": None, "last_summary_point_triggered": None })

    def prompt_load_file_via_eve(self):
        self._eve_speak("يرجى اختيار ملف بروتوكول UCP JSON الخاص بك.", is_system=True); self.master.after(200, self._actually_show_file_dialog_for_eve)

    def _actually_show_file_dialog_for_eve(self):
        filepath = filedialog.askopenfilename(title="اختر ملف UCP JSON", filetypes=(("ملفات JSON", "*.json"),("جميع الملفات", "*.*")))
        if self.load_ucp_file(filepath_from_eve=filepath):
            self.eve_state["initial_data_loaded_for_eve"] = True; self.eve_state["is_editing_specific_section_now"] = False
            self._reset_eve_progress_for_new_protocol(); self.ask_for_mental_state_update()
        elif self.eve_state["current_mode"] == "PROCESSING_FILE_LOAD": self.start_eve_interaction()

    def ask_for_mental_state_update(self):
        self.eve_state["current_mode"] = "AWAITING_MENTAL_STATE_CHOICE"; self.eve_state["is_asking_mental_state"] = True
        self._update_current_mental_state_cache_from_data(); current_mental_state_text = "غير محددة"
        mental_state_section = SECTION_TYPE_DATA.get("mental_state", {})
        ms_field_def = mental_state_section.get("fields", [{}])[0] if mental_state_section else {}
        ms_options = ms_field_def.get("options", [])
        for opt in ms_options:
            if opt.get("value") == self.current_mental_state_cache: current_mental_state_text = opt.get("text","غير محددة"); break
        self._eve_speak(f"مرحباً يا {self.eve_preferred_name_cache}. قبل أن نبدأ، كيف هي حالتك الذهنية اليوم؟", for_mental_state_selection=True)
        if self.current_mental_state_cache != "not_specified" and self.eve_state["initial_data_loaded_for_eve"]: self._eve_speak(f"(حالتك المسجلة سابقاً هي: '{current_mental_state_text}')", is_system=True, for_mental_state_selection=True)
        self.eve_current_question_label.config(text="يرجى تحديد حالتك الذهنية الحالية:")
        [w.destroy() for w in self.eve_mcq_options_frame.winfo_children()]
        if not ms_options: self._eve_speak("خطأ: لم يتم العثور على خيارات الحالة الذهنية.", is_system=True); return
        for option_config in ms_options:
            if option_config.get("value") == "": continue
            btn = ttk.Button(self.eve_mcq_options_frame, text=option_config.get("text"), style="Eve.TButton", command=lambda choice_val=option_config.get("value"), choice_text=option_config.get("text"): self._process_mental_state_choice(choice_val, choice_text))
            btn.pack(fill=tk.X, pady=2)
        self._eve_manage_input_visibility(show_mcq_options=True, show_send=False, show_skip=False); self.eve_mcq_options_frame.pack(fill=tk.X, pady=(5,8))

    def _process_mental_state_choice(self, choice_value: str, choice_text: str):
        self.eve_state["is_asking_mental_state"] = False; [w.destroy() for w in self.eve_mcq_options_frame.winfo_children()]; self.eve_mcq_options_frame.pack_forget()
        self.current_mental_state_cache = choice_value; self._eve_speak(f"أنت: اخترت '{choice_text}' كحالتك الذهنية.", is_user=True)
        if not self.loaded_ucp_data: self.loaded_ucp_data = {"sections": []} # Safety, should exist
        ms_section_def = SECTION_TYPE_DATA.get("mental_state",{}) # Get static definition
        ms_section_list = self.loaded_ucp_data.setdefault("sections", [])
        ms_section_data = next((s for s in ms_section_list if s.get("id") == "mental_state"), None)
        if not ms_section_data: ms_section_data = {"id": "mental_state", "title": ms_section_def.get("title", "🧠 الحالة الذهنية"), "items": [{}]}; ms_section_list.append(ms_section_data)
        elif not ms_section_data.get("items") or not isinstance(ms_section_data.get("items"), list) or len(ms_section_data.get("items")) == 0: ms_section_data["items"] = [{}]
        elif not isinstance(ms_section_data["items"][0], dict): ms_section_data["items"][0] = {} # If item exists but not a dict
        ms_section_data["items"][0]["selectedMentalState"] = choice_value
        if "mentalStateNotes" not in ms_section_data["items"][0]: ms_section_data["items"][0]["mentalStateNotes"] = ""
        self._set_data_changed(True); self.eve_state["current_mode"] = "PROCESSING_PROTOCOL"
        greeting_phrases_map = EVE_MENTAL_STATE_PHRASES.get(self.current_mental_state_cache, EVE_MENTAL_STATE_PHRASES["not_specified"])
        adaptive_greeting = random.choice(greeting_phrases_map["greetings"]).format(name=self.eve_preferred_name_cache); self._eve_speak(adaptive_greeting)
        self.ask_next_eve_question()

    def _get_current_mental_state_from_data(self) -> Optional[str]:
        if not self.loaded_ucp_data or not self.loaded_ucp_data.get("sections"): return None
        ms_section = next((s for s in self.loaded_ucp_data["sections"] if s.get("id") == "mental_state"), None)
        if ms_section and ms_section.get("items") and isinstance(ms_section.get("items"),list) and len(ms_section.get("items")) > 0 and isinstance(ms_section.get("items")[0],dict): return ms_section["items"][0].get("selectedMentalState")
        return None

    def _update_current_mental_state_cache_from_data(self):
        self.current_mental_state_cache = self._get_current_mental_state_from_data() or "not_specified"

    def get_eve_greeting(self):
        hour = datetime.datetime.now().hour;
        if hour < 12: return "صباح الخير"
        if hour < 18: return "نهارك سعيد"
        return "مساء الخير"

    def _eve_manage_input_visibility(self, show_entry=False, show_text=False, show_select=False, show_mcq_options=False, show_tf_options=False, show_templates_combobox=False, show_send=True, show_skip=True, show_add_another=False, show_done_section=False, show_summary_confirm_buttons=False, show_analysis_display=False, show_analysis_confirm_buttons=False):
        self.eve_reply_entry.pack_forget(); self.eve_reply_text.pack_forget(); self.eve_reply_combobox.pack_forget()
        self.eve_summary_confirm_frame.pack_forget(); [w.destroy() for w in self.eve_summary_confirm_frame.winfo_children()]
        self.eve_analysis_display_text.pack_forget(); self.eve_analysis_confirm_frame.pack_forget(); [w.destroy() for w in self.eve_analysis_confirm_frame.winfo_children()]
        self.eve_add_another_button.pack_forget(); self.eve_done_section_button.pack_forget()
        self.eve_templates_combobox.pack_forget(); self.eve_template_select_var.set("")
        if show_templates_combobox: self.eve_templates_combobox.pack(side=tk.TOP, fill=tk.X, pady=(0,5), in_=self.eve_template_combobox_frame)
        if show_mcq_options or show_tf_options: self.eve_mcq_options_frame.pack(fill=tk.X, pady=(5,8))
        if show_entry: self.eve_reply_entry.pack(fill=tk.X, expand=True, pady=(0,3)); self.eve_reply_entry.focus_set()
        if show_text: self.eve_reply_text.pack(fill=tk.X, expand=True, pady=(0,3)); self.eve_reply_text.focus_set()
        if show_select: self.eve_reply_combobox.pack(fill=tk.X, expand=True, pady=(0,3)); self.eve_reply_combobox.focus_set()
        self.eve_send_button.config(state=tk.NORMAL if show_send else tk.DISABLED)
        self.eve_skip_button.config(state=tk.NORMAL if show_skip else tk.DISABLED)
        if show_add_another: self.eve_add_another_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X, in_=self.eve_multi_action_frame)
        if show_done_section: self.eve_done_section_button.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X, in_=self.eve_multi_action_frame)
        if show_summary_confirm_buttons:
            self.eve_summary_confirm_frame.pack(fill=tk.X, pady=(8,0))
            yes_btn = ttk.Button(self.eve_summary_confirm_frame, text="✅ نعم، هذا صحيح. لنكمل!", style="Eve.TButton", command=lambda: self.process_eve_reply(mcq_choice="summary_yes"))
            yes_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            no_btn = ttk.Button(self.eve_summary_confirm_frame, text="❌ لا، أريد التوضيح/التعديل.", command=lambda: self.process_eve_reply(mcq_choice="summary_no"))
            no_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        if show_analysis_display:
            self.eve_analysis_display_text.pack(fill=tk.BOTH, expand=True, pady=(5,10))
            self.eve_analysis_display_text.config(state=tk.NORMAL); self.eve_analysis_display_text.delete("1.0", tk.END)
            analysis_content = self.eve_state.get("api_analysis_result", "لم يتم استلام تحليل.")
            self.eve_analysis_display_text.insert(tk.END, analysis_content); self.eve_analysis_display_text.config(state=tk.DISABLED)
        if show_analysis_confirm_buttons:
            self.eve_analysis_confirm_frame.pack(fill=tk.X, pady=(8,0))
            save_analysis_btn = ttk.Button(self.eve_analysis_confirm_frame, text="💾 حفظ هذا التحليل في البروتوكول", style="Eve.TButton", command=lambda: self.process_eve_reply(mcq_choice="analysis_save"))
            save_analysis_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            discard_analysis_btn = ttk.Button(self.eve_analysis_confirm_frame, text="🗑️ تجاهل هذا التحليل والمتابعة", command=lambda: self.process_eve_reply(mcq_choice="analysis_discard"))
            discard_analysis_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)

    def _on_template_selected_from_combobox(self, event=None):
        sel_template = self.eve_template_select_var.get(); prompt_text = "[اختر اقتراحًا أو اكتب أدناه]"
        if sel_template and sel_template != prompt_text:
            ctx = self.eve_state["current_question_context"]
            if ctx and ctx["type"] == "direct":
                f_type = ctx["field_def"]["type"]; target_widget = self.eve_reply_text if f_type == "textarea" else (self.eve_reply_entry if f_type == "text" else None)
                if target_widget:
                    if isinstance(target_widget, tk.Text): target_widget.delete("1.0",tk.END); target_widget.insert("1.0",sel_template)
                    elif isinstance(target_widget, ttk.Entry): target_widget.delete(0,tk.END); target_widget.insert(0,sel_template)
                    target_widget.focus_set()
        self.eve_template_select_var.set(prompt_text)

    def _eve_show_input_type(self, field_def: Optional[Dict], iq_config: Optional[Dict], is_asking_add_another:bool=False, is_session_end:bool=False):
        self.eve_reply_entry.delete(0, tk.END); self.eve_reply_text.delete("1.0", tk.END)
        if hasattr(self.eve_reply_text,'tag_remove'): self.eve_reply_text.tag_remove("placeholder_italic", "1.0", tk.END)
        self.eve_reply_select_var.set(""); self.eve_reply_combobox.set(""); self.eve_reply_combobox['values'] = []
        self.eve_templates_combobox['values'] = []; self.eve_template_select_var.set("")
        [w.destroy() for w in self.eve_mcq_options_frame.winfo_children()]; show_templates_cb = False # Clear first
        if is_session_end: self._eve_manage_input_visibility(show_send=False, show_skip=False, show_analysis_display=False, show_analysis_confirm_buttons=False); self.eve_current_question_label.config(text="اكتمل التفاعل!"); self._eve_speak("يمكنك الحفظ أو بدء تفاعل جديد.",is_system=True); return
        if is_asking_add_another: self._eve_manage_input_visibility(show_send=False,show_skip=False,show_add_another=True,show_done_section=True); return
        default_template_prompt = "[اختر اقتراحًا أو اكتب أدناه]"
        if field_def and (field_def["type"] == "text" or field_def["type"] == "textarea") and field_def.get("templates"): templates = [default_template_prompt] + field_def.get("templates", []); self.eve_templates_combobox['values'] = templates; self.eve_template_select_var.set(templates[0]); show_templates_cb = True
        if iq_config:
            self.eve_state["current_question_context"] = {"type": "invented", "iq_config": iq_config}; iq_type = iq_config["type"]
            if iq_type == "mc": [ttk.Button(self.eve_mcq_options_frame, text=opt_text, style="Eve.TButton" if len(opt_text)<35 else "TButton", command=lambda c=opt_text: self.process_eve_reply(mcq_choice=c)).pack(side=tk.TOP, fill=tk.X, pady=2) for opt_text in iq_config["options"]]; self._eve_manage_input_visibility(show_mcq_options=True, show_send=False, show_skip=True, show_templates_combobox=show_templates_cb)
            elif iq_type == "tf": ttk.Button(self.eve_mcq_options_frame, text="✅ صحيح/نعم", style="Eve.TButton", command=lambda: self.process_eve_reply(mcq_choice="True")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2); ttk.Button(self.eve_mcq_options_frame, text="❌ خطأ/لا", style="Eve.TButton", command=lambda: self.process_eve_reply(mcq_choice="False")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2); self._eve_manage_input_visibility(show_tf_options=True, show_send=False, show_skip=True, show_templates_combobox=show_templates_cb)
            elif iq_type == "textarea": self._eve_manage_input_visibility(show_text=True, show_templates_combobox=show_templates_cb); self.eve_reply_text.insert("1.0",iq_config.get("placeholder",""),"placeholder_italic")
            else: self._eve_manage_input_visibility(show_entry=True, show_templates_combobox=show_templates_cb); self.eve_reply_entry.insert(0,iq_config.get("placeholder",""))
        elif field_def:
            sec_key = self.eve_state["section_keys_order"][self.eve_state["current_section_key_index"]]; item_idx = self.eve_state["current_item_count_for_section"] -1 if self.eve_state["current_item_count_for_section"] > 0 else 0; self.eve_state["current_question_context"] = {"type": "direct", "section_key": sec_key, "field_def": field_def, "item_index": item_idx}; curr_val = self._get_eve_current_field_value(sec_key, item_idx, field_def["jsonKey"])
            if field_def["type"] == "textarea": self._eve_manage_input_visibility(show_text=True, show_templates_combobox=show_templates_cb); self.eve_reply_text.insert("1.0",str(curr_val) if curr_val is not None else (field_def.get("placeholder_text_area","") if show_templates_cb else ""),"placeholder_italic" if curr_val is None and show_templates_cb and field_def.get("placeholder_text_area") else "")
            elif field_def["type"] == "select":
                opts_display = [opt['text'] for opt in field_def.get("options",[]) if opt.get('text')]; self.eve_reply_combobox['values']=opts_display; sel_found=False
                if curr_val is not None:
                    for opt_cfg in field_def.get("options",[]):
                        if opt_cfg.get('value')==curr_val: self.eve_reply_select_var.set(opt_cfg.get('text')); sel_found=True; break
                if not sel_found and opts_display:
                    try: self.eve_reply_combobox.current(0)
                    except tk.TclError: pass
                self._eve_manage_input_visibility(show_select=True,show_templates_combobox=False)
            else: self._eve_manage_input_visibility(show_entry=True, show_templates_combobox=show_templates_cb); self.eve_reply_entry.insert(0,str(curr_val) if curr_val is not None else "")
        else: self._eve_manage_input_visibility(show_send=False,show_skip=False); self.eve_current_question_label.config(text="أنا مرتبكة. لنجرب مجددًا."); self.master.after(1000,self.start_eve_interaction)
        if hasattr(self.eve_reply_text,'tag_configure'): self.eve_reply_text.tag_configure("placeholder_italic", foreground="grey", font=(self.eve_bubble_font[0], self.eve_bubble_font[1], "italic"))

    def _get_eve_current_field_value(self, section_key, item_idx, json_key_to_check):
        if not self.loaded_ucp_data or not self.loaded_ucp_data.get("sections"): return None
        target_section = next((s for s in self.loaded_ucp_data["sections"] if s.get("id") == section_key), None)
        if target_section and "items" in target_section and isinstance(target_section["items"], list) and 0 <= item_idx < len(target_section["items"]):
            if isinstance(target_section["items"][item_idx], dict): return target_section["items"][item_idx].get(json_key_to_check)
        return None

    def ask_next_eve_question(self):
        if self.eve_state["current_mode"] == "AWAITING_SUMMARY_CONFIRMATION" or self.eve_state["is_asking_mental_state"] or self.eve_state["is_waiting_for_api_response"]: return

        current_section_key_completed = None
        if self.eve_state["current_mode"] == "PROCESSING_PROTOCOL":
            # Determine if a section was just completed (i.e., current_field_index is 0 AND we are not at the very start)
            if self.eve_state["current_field_index"] == 0 and self.eve_state["current_item_count_for_section"] <= 1 : # If single item section or first item of multi-item section
                 if self.eve_state["current_section_key_index"] > 0 : # Ensure we are not at the beginning of the first section
                    current_section_key_completed = self.eve_state["section_keys_order"][self.eve_state["current_section_key_index"] -1]

        summary_key_to_trigger = None
        summary_points = self.eve_state["summary_points"]
        if current_section_key_completed:
            if current_section_key_completed == summary_points["summary_1_after"] and self.eve_state["last_summary_point_triggered"] != "summary_1": summary_key_to_trigger = "summary_1"
            elif current_section_key_completed == summary_points["summary_2_after"] and self.eve_state["last_summary_point_triggered"] != "summary_2": summary_key_to_trigger = "summary_2"
            elif current_section_key_completed == summary_points["summary_3_after"] and self.eve_state["last_summary_point_triggered"] != "summary_3": summary_key_to_trigger = "summary_3"
        
        if summary_key_to_trigger:
            self.eve_state["last_summary_point_triggered"] = summary_key_to_trigger
            self._eve_present_summary_and_ask_confirmation(summary_key_to_trigger); return

        if self.eve_state["current_mode"] != "PROCESSING_PROTOCOL" and self.eve_state["current_mode"] != "PROCESSING_INVENTED":
            if self.eve_state["current_mode"] == "AWAITING_INITIAL_CHOICE": self.start_eve_interaction()
            return
        if self.eve_state["is_asking_to_add_another"]: return

        section_key = self.get_current_eve_section_key()
        if section_key:
            section_def_data = SECTION_TYPE_DATA.get(section_key)
            if not section_def_data: self._eve_speak(f"خطأ: لا يوجد تعريف للقسم {section_key}. جاري التخطي.", is_system=True); self.move_to_next_eve_direct_section_or_invented(); return
            is_multi_item = section_def_data.get("maxItems", 1) > 1 or section_def_data.get("maxItems") is None
            field_def = self.get_current_eve_field_def()
            if field_def:
                item_num_access = self.eve_state["current_item_count_for_section"] or 1; data_item_idx = item_num_access - 1; should_skip = False
                if self.eve_state["initial_data_loaded_for_eve"] and not self.eve_state["is_editing_specific_section_now"]:
                    existing_val = self._get_eve_current_field_value(section_key, data_item_idx, field_def["jsonKey"]);
                    if existing_val is not None:
                        is_empty_skip = (field_def["type"]=="select" and (not bool(existing_val) or (field_def.get("options") and existing_val==field_def.get("options",[{}])[0].get("value")))) or \
                                        (isinstance(existing_val,str) and not bool(existing_val.strip()))
                        if not is_empty_skip: should_skip=True
                if should_skip: self.eve_state["current_field_index"] +=1; self.master.after(10,self.ask_next_eve_question); return
                proto_sec = next((s for s in self.loaded_ucp_data.get("sections",[]) if s.get("id")==section_key),None)
                if not proto_sec: proto_sec={"id":section_key, "title":section_def_data["title"], "items":[]}; self.loaded_ucp_data.setdefault("sections",[]).append(proto_sec)
                eff_item_num_user = self.eve_state["current_item_count_for_section"] or 1; self.eve_state["current_item_count_for_section"]=eff_item_num_user
                items_list = proto_sec.setdefault("items",[]); [items_list.append({}) for _ in range(eff_item_num_user - len(items_list))]
                item_indicator = f" (العنصر {eff_item_num_user})" if is_multi_item and eff_item_num_user > 0 else ""
                clean_title = section_def_data['title'].strip().lstrip('👤🏠🎓🧠💡⚖️👁️🛠️🌟🧐📌🧪🔗🎭📚💬⚙️🧭🗣️🚫💾🤔🏅📝 ')
                question_text_main = f"بالنسبة لـ '{clean_title}{item_indicator}'، ماذا عن: {field_def['label']}؟ 📝"
                self._eve_speak(question_text_main); self.eve_current_question_label.config(text=field_def['label'] + ":"); self._eve_show_input_type(field_def, None)
            else: # Finished fields for item
                if self.eve_state["is_editing_specific_section_now"]: self._eve_speak(f"أنهينا مراجعة قسم '{section_def_data['title'].strip().lstrip('👤🏠🎓🧠💡⚖️👁️🛠️🌟🧐📌🧪🔗🎭📚💬⚙️🧭🗣️🚫💾🤔🏅📝 ')}'.", is_system=True); self.eve_state["is_editing_specific_section_now"]=False
                max_items=section_def_data.get("maxItems", float('inf')); curr_item_num = self.eve_state["current_item_count_for_section"] or 1
                if not is_multi_item or curr_item_num >= max_items : self.move_to_next_eve_direct_section_or_invented() # Summary will be checked inside move_to_next
                else: self.eve_state["is_asking_to_add_another"]=True; self._eve_speak(f"هل تود إضافة عنصر آخر إلى '{section_def_data['title'].strip().lstrip('👤🏠🎓🧠💡⚖️👁️🛠️🌟🧐📌🧪🔗🎭📚💬⚙️🧭🗣️🚫💾🤔🏅📝 ')}'?"); self.eve_current_question_label.config(text=f"إضافة المزيد؟"); self._eve_show_input_type(None,None,is_asking_add_another=True)
        else: # All direct sections done
            if self.eve_state["is_editing_specific_section_now"]: self._eve_speak("أنهينا مراجعة جميع الأقسام.", is_system=True); self.eve_state["is_editing_specific_section_now"]=False
            if self.eve_state["summary_points"]["summary_4_before_invented"] and self.eve_state["last_summary_point_triggered"] != "summary_4":
                self.eve_state["last_summary_point_triggered"] = "summary_4"; self._eve_present_summary_and_ask_confirmation("summary_4"); return
            if self.eve_state["current_mode"] != "PROCESSING_INVENTED": self.eve_state["current_mode"] = "PROCESSING_INVENTED"
            self.eve_state["current_invented_question_index"] +=1; idx = self.eve_state["current_invented_question_index"]
            if 0 <= idx < len(EVE_INVENTED_QUESTIONS):
                iq = EVE_INVENTED_QUESTIONS[idx]; should_skip_iq=False
                if self.eve_state["initial_data_loaded_for_eve"] and not self.eve_state["is_editing_specific_section_now"]:
                    notes_sec_def = SECTION_TYPE_DATA.get("additional_notes"); notes_text_content=""
                    if notes_sec_def and self.loaded_ucp_data:
                        data_notes_sec = next((s for s in self.loaded_ucp_data.get("sections",[]) if s.get("id")=="additional_notes"), None)
                        if data_notes_sec and data_notes_sec.get("items") and isinstance(data_notes_sec["items"],list) and data_notes_sec["items"] and notes_sec_def.get("fields"):
                            notes_json_key_field = notes_sec_def["fields"][0].get("jsonKey")
                            if isinstance(data_notes_sec["items"][0],dict): notes_text_content=data_notes_sec["items"][0].get(notes_json_key_field,"")
                    normalized_iq_question_for_search = iq['question'].replace('"', "'")
                    q_identifier = f"Eve 🧚 (Q: \"{normalized_iq_question_for_search}\"):"
                    if q_identifier in notes_text_content: should_skip_iq=True
                if should_skip_iq: self.master.after(10, self.ask_next_eve_question); return
                self._eve_speak(iq["question"]); self.eve_current_question_label.config(text="سؤال إبداعي من إيفي 🧚:"); self._eve_show_input_type(None, iq)
            else: # All invented questions done
                self.eve_state["current_mode"] = "AWAITING_API_ANALYSIS_CHOICE"
                self._eve_speak(f"رائع يا {self.eve_preferred_name_cache}! ✨ لقد استكملنا كل شيء. بروتوكولك جاهز!"); self._eve_speak("هل ترغب في أن أقوم بإرسال هذا البروتوكول إلى نموذج لغوي خارجي لتحليله وتقديم ملخص لرؤى حول شخصيتك وأنماطك؟ هذا التحليل سيُضاف إلى بروتوكولك.")
                self.eve_current_question_label.config(text="هل تود إجراء تحليل خارجي الآن؟"); self._eve_manage_input_visibility(show_send=False, show_skip=False); [w.destroy() for w in self.eve_mcq_options_frame.winfo_children()]
                yes_btn = ttk.Button(self.eve_mcq_options_frame, text="✅ نعم، قم بالتحليل التلقائي الآن", style="Eve.TButton", command=lambda: self.process_eve_reply(mcq_choice="api_analyze_yes")); yes_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=3)
                no_btn = ttk.Button(self.eve_mcq_options_frame, text="❌ لا، شكرًا (سأنهي الجلسة)", style="TButton", command=lambda: self.process_eve_reply(mcq_choice="api_analyze_no")); no_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=3)
                self.eve_mcq_options_frame.pack(fill=tk.X, pady=(5,8))

    def get_current_eve_section_key(self) -> Optional[str]:
        idx = self.eve_state["current_section_key_index"]; keys = self.eve_state["section_keys_order"]; return keys[idx] if 0 <= idx < len(keys) else None

    def get_current_eve_field_def(self) -> Optional[Dict]:
        sec_key = self.get_current_eve_section_key()
        if sec_key: sec_def = SECTION_TYPE_DATA.get(sec_key)
        if sec_key and sec_def: fields = sec_def.get("fields",[]); field_idx = self.eve_state["current_field_index"]; return fields[field_idx] if 0 <= field_idx < len(fields) else None
        return None

    def move_to_next_eve_direct_section_or_invented(self):
        self.eve_state["current_section_key_index"] +=1
        self.eve_state["current_field_index"] = 0; self.eve_state["current_item_count_for_section"] = 0
        # Check for summary AFTER incrementing index, to summarize section just left
        completed_section_index = self.eve_state["current_section_key_index"] -1 # Index of the section we just finished
        if completed_section_index >= 0:
            completed_section_key = self.eve_state["section_keys_order"][completed_section_index]
            summary_key_to_trigger = None
            summary_points = self.eve_state["summary_points"]
            if completed_section_key == summary_points["summary_1_after"] and self.eve_state["last_summary_point_triggered"] != "summary_1": summary_key_to_trigger = "summary_1"
            elif completed_section_key == summary_points["summary_2_after"] and self.eve_state["last_summary_point_triggered"] != "summary_2": summary_key_to_trigger = "summary_2"
            elif completed_section_key == summary_points["summary_3_after"] and self.eve_state["last_summary_point_triggered"] != "summary_3": summary_key_to_trigger = "summary_3"
            if summary_key_to_trigger:
                self.eve_state["last_summary_point_triggered"] = summary_key_to_trigger
                self._eve_present_summary_and_ask_confirmation(summary_key_to_trigger)
                return # Wait for summary confirmation before asking next actual question
        self.ask_next_eve_question()


    def eve_handle_add_another(self):
        self.eve_state["is_asking_to_add_another"]=False; self.eve_state["current_field_index"]=0; self.eve_state["current_item_count_for_section"] +=1; self.eve_state["initial_data_loaded_for_eve"]=False
        self._eve_speak("حسناً، لنضف عنصراً آخر!", is_user=True); self.ask_next_eve_question()

    def eve_handle_done_with_section(self): # Modified to integrate summary check
        self.eve_state["is_asking_to_add_another"]=False
        completed_section_key = self.get_current_eve_section_key()
        summary_key_to_trigger = None
        summary_points = self.eve_state["summary_points"]
        if completed_section_key == summary_points["summary_1_after"] and self.eve_state["last_summary_point_triggered"] != "summary_1": summary_key_to_trigger = "summary_1"
        elif completed_section_key == summary_points["summary_2_after"] and self.eve_state["last_summary_point_triggered"] != "summary_2": summary_key_to_trigger = "summary_2"
        elif completed_section_key == summary_points["summary_3_after"] and self.eve_state["last_summary_point_triggered"] != "summary_3": summary_key_to_trigger = "summary_3"

        if summary_key_to_trigger:
            self.eve_state["last_summary_point_triggered"] = summary_key_to_trigger
            self._eve_present_summary_and_ask_confirmation(summary_key_to_trigger)
            # After confirmation, if user says yes, process_eve_reply will call ask_next_eve_question,
            # which will then effectively call move_to_next_eve_direct_section_or_invented to move to next actual section.
        else:
             self._eve_speak("موافق، ننتقل للقسم التالي.", is_user=True)
             self.move_to_next_eve_direct_section_or_invented()


    def _eve_generate_summary(self, summary_config_key: str) -> str:
        summary_parts = []; summary_configs = {
            "summary_1": [ ("personal", "preferredName", "direct", "اسمك المفضل للتفاعل هو: {value}."), ("social", "socialFamilyDetails", "mention_if_filled", "وقد شاركت بعض التفاصيل حول وضعك الاجتماعي."), ("educational_professional", "educationalBackground", "first_n_words(20)", "فيما يتعلق بخلفيتك التعليمية، ذكرتَ: '{value}...'.") , ("educational_professional", "professionalExperience", "first_n_words(20)", "وفيما يخص خبراتك المهنية، أشرتَ إلى: '{value}...'.") ],
            "summary_2": [ ("thinking_reference", "coreThinkingReferenceDescription", "direct", "مرجعيتك الفكرية هي: {value}."), ("cognitive_passion", "cognitivePassionName", "first_item_direct", "من اهتماماتك المعرفية: {value}."), ("ethical_values", "ethicalValueName", "first_item_direct", "من قيمك الأساسية: {value}."), ("concepts_perspective", "coreConceptName", "first_item_direct", "لديك منظور خاص تجاه مفهوم: {value}.") ],
            "summary_3": [ ("cognitive_tools_methodology", "cognitiveToolName", "first_item_direct", "من الأدوات المعرفية التي تستخدمها: {value}."), ("inspiring_figures", "inspiringFigureName", "first_item_direct", "من الشخصيات الملهمة لك: {value}."), ("projects", "projectOrObjectiveTitle", "first_item_direct", "أحد مشاريعك الحالية هو: '{value}'."), ("projects", "projectDetailedGoals", "first_item_first_n_words(15)", "ويهدف بشكل رئيسي إلى: '{value}...'.") ],
            "summary_4": [ ("role", "llmPrimaryRole", "direct", "يبدو أنك تفضل أن يكون دوري كـ: {value}."), ("interaction_style", "preferredResponseStyle", "first_n_words(15)", "وتفضل أن يكون أسلوب تفاعلي معك: '{value}...'.") , ("memory_management_directives", "contextMaintenanceDirective", "first_n_words(15)", "وفيما يتعلق بإدارة الذاكرة، أشرت إلى: '{value}...'.")] }; current_config = summary_configs.get(summary_config_key, [])
        for section_id, json_key, process_method, template_str in current_config:
            section_data = next((s for s in self.loaded_ucp_data.get("sections", []) if s.get("id") == section_id), None); value_to_display = None
            if section_data and section_data.get("items"):
                items = section_data.get("items", []); target_item = items[0] if items and isinstance(items[0],dict) else None
                if target_item:
                    raw_value = target_item.get(json_key)
                    if raw_value is not None and str(raw_value).strip():
                        if process_method == "direct" or process_method == "first_item_direct": value_to_display = str(raw_value)
                        elif process_method == "mention_if_filled": value_to_display = "نعم"
                        elif "first_n_words" in process_method or "first_item_first_n_words" in process_method: n_str = process_method.split("(")[1].split(")")[0] if "(" in process_method else "15"; n = int(n_str) if n_str.isdigit() else 15; value_to_display = " ".join(str(raw_value).split()[:n])
            if value_to_display:
                if process_method == "mention_if_filled": summary_parts.append(template_str.split(":")[0].strip() + ".")
                else: summary_parts.append(template_str.format(value=value_to_display))
        if not summary_parts: return "يبدو أننا لم نغط الكثير من التفاصيل بعد في هذه الأقسام."
        final_summary_text = "\n- " + "\n- ".join(summary_parts); return final_summary_text

    def _eve_present_summary_and_ask_confirmation(self, summary_config_key: str):
        self.eve_state["current_mode"] = "AWAITING_SUMMARY_CONFIRMATION"; self.eve_state["current_question_context"] = {"type": "summary_confirm", "summary_key": summary_config_key}
        summary_text_core = self._eve_generate_summary(summary_config_key); mental_state_phrases_map = EVE_MENTAL_STATE_PHRASES.get(self.current_mental_state_cache, EVE_MENTAL_STATE_PHRASES["not_specified"])
        adaptive_summary_intro = mental_state_phrases_map.get("summary_intro", "دعنا نتأكد أنني فهمتك بشكل صحيح:") + f" يا {self.eve_preferred_name_cache}!"; full_summary_message = adaptive_summary_intro + summary_text_core
        self._eve_speak(full_summary_message); self.eve_current_question_label.config(text="هل هذا الملخص صحيح ويعكس ما ذكرته؟"); self._eve_manage_input_visibility(show_send=False, show_skip=False, show_summary_confirm_buttons=True)

    def process_eve_reply(self, mcq_choice: Optional[str] = None):
        # --- Summary Confirmation Logic ---
        if self.eve_state["current_mode"] == "AWAITING_SUMMARY_CONFIRMATION":
            ctx = self.eve_state["current_question_context"]
            if ctx and ctx["type"] == "summary_confirm":
                self._eve_manage_input_visibility(show_send=False, show_skip=False, show_summary_confirm_buttons=False)
                if mcq_choice == "summary_yes":
                    self._eve_speak("رائع! يسعدني أننا متفقون. لنواصل.", is_user=True)
                    next_mode_after_summary = "PROCESSING_PROTOCOL"
                    if ctx.get("summary_key") == "summary_4": # Summary before Invented Questions or API
                        # Check if we need to go to Invented Questions or directly to API choice
                        if self.eve_state.get("current_invented_question_index", -1) < len(EVE_INVENTED_QUESTIONS) -1 :
                             next_mode_after_summary = "PROCESSING_INVENTED"
                        else: # All IQs are done or skipped, move to API choice
                             next_mode_after_summary = "AWAITING_API_ANALYSIS_CHOICE" # Placeholder until API mode fully decided

                    self.eve_state["current_mode"] = next_mode_after_summary
                    
                    # Logic to correctly advance after summary
                    if ctx.get("summary_key") != "summary_4" and next_mode_after_summary == "PROCESSING_PROTOCOL":
                         # This means we summarized mid-protocol sections.
                         # The current_section_key_index was already advanced before summary was triggered
                         # OR if triggered by eve_handle_done_with_section, then move_to_next will advance.
                         # A safer bet is to just call ask_next_eve_question which will pick up
                         # from the current_section_key_index and current_field_index.
                         # If a section just finished and triggered a summary, process_eve_reply for that summary's 'yes'
                         # should correctly allow ask_next_eve_question to proceed to the *next* section's first question.
                         self.ask_next_eve_question()
                    elif next_mode_after_summary == "PROCESSING_INVENTED":
                         self.ask_next_eve_question() # Will start asking IQs
                    elif next_mode_after_summary == "AWAITING_API_ANALYSIS_CHOICE":
                         # Directly trigger the API choice logic as all IQs are done
                         self.eve_state["current_invented_question_index"] = len(EVE_INVENTED_QUESTIONS) # Mark IQs as done
                         self.ask_next_eve_question() # This should now lead to API choice
                    else:
                         self.ask_next_eve_question()


                elif mcq_choice == "summary_no":
                    self._eve_speak("أتفهم ذلك. لا مشكلة.", is_user=True)
                    self._eve_speak("يمكنك استخدام خيار '✏️ Edit Specific Section...' من قائمة 'Eve' لتعديل الأقسام.")
                    self.eve_current_question_label.config(text="يمكنك تعديل الأقسام من قائمة 'Eve'.")
                    self.eve_state["current_mode"] = "USER_CORRECTING_SUMMARY" # Halt Eve's automatic progression
                return # Crucial return for summary handling
        
        # --- API Analysis Choice Logic ---
        elif self.eve_state["current_mode"] == "AWAITING_API_ANALYSIS_CHOICE":
            self._eve_manage_input_visibility(show_mcq_options=False, show_send=False, show_skip=False) # Hide choice buttons
            if mcq_choice == "api_analyze_yes":
                self._eve_speak("طلبت إجراء تحليل خارجي تلقائي.", is_user=True)
                self.trigger_external_analysis() # This will change mode to WAITING_FOR_API_RESPONSE
            elif mcq_choice == "api_analyze_no":
                self._eve_speak("اخترت عدم إجراء تحليل خارجي الآن.", is_user=True)
                self.eve_state["current_mode"] = "SESSION_COMPLETE"
                self._eve_speak("بروتوكولك جاهز. يمكنك حفظه الآن من قائمة 'File'. شكرًا لك!", is_system=True)
                self.eve_current_question_label.config(text="اكتملت الجلسة!")
                self._eve_manage_input_visibility(show_send=False, show_skip=False)
            return # Crucial return for API choice handling

        # --- API Analysis Save/Discard Choice Logic ---
        elif self.eve_state["current_mode"] == "AWAITING_API_ANALYSIS_SAVE_CHOICE":
             self._eve_manage_input_visibility(show_analysis_display=False, show_analysis_confirm_buttons=False, show_send=False, show_skip=False) # Hide all

             if mcq_choice == "analysis_save":
                self._eve_speak("طلبت حفظ التحليل في البروتوكول.", is_user=True)
                if self.eve_state.get("api_analysis_result"):
                    self._save_external_analysis_to_protocol(self.eve_state["api_analysis_result"])
                    self._eve_speak("تم حفظ ملخص التحليل الخارجي بنجاح في قسم الملاحظات الإضافية.", is_system=True)
                else:
                    self._eve_speak("لم يتم العثور على نتيجة تحليل لحفظها.", is_system=True)
             elif mcq_choice == "analysis_discard":
                self._eve_speak("اخترت تجاهل هذا التحليل.", is_user=True)
             
             self.eve_state["current_mode"] = "SESSION_COMPLETE"
             self.eve_state["api_analysis_result"] = None # Clear result
             self._eve_speak("بروتوكولك جاهز (مع أو بدون التحليل المضاف). يمكنك حفظه الآن من قائمة 'File'. شكرًا لك!", is_system=True)
             self.eve_current_question_label.config(text="اكتملت الجلسة!")
             # Ensure no inputs are visible:
             self._eve_manage_input_visibility(show_entry=False, show_text=False, show_select=False, 
                                              show_mcq_options=False, show_tf_options=False, 
                                              show_templates_combobox=False, show_send=False, show_skip=False,
                                              show_add_another=False, show_done_section=False,
                                              show_summary_confirm_buttons=False,
                                              show_analysis_display=False, show_analysis_confirm_buttons=False)
             return # Crucial return for save/discard analysis choice

        # --- Regular Question Reply Processing (the part you highlighted) ---
        context = self.eve_state.get("current_question_context") # Use .get for safety

        if not context:
            self._eve_speak("خطأ: السياق الحالي للسؤال غير محدد. سأحاول إعادة تحميل السؤال الأخير أو بدء التفاعل من جديد.", is_system=True)
            # Decide recovery strategy
            if self.eve_state["current_mode"] in ["PROCESSING_PROTOCOL", "PROCESSING_INVENTED"] and self.eve_state["current_section_key_index"] < len(self.eve_state["section_keys_order"]):
                self.ask_next_eve_question() # Try to re-ask
            else:
                self.start_eve_interaction() # Fallback to full restart
            return

        reply_val_store = ""
        display_reply_bubble = ""
        source_widget = None

        if context.get("type") == "invented":
            iq_config = context.get("iq_config", {})
            if iq_config.get("type") == "textarea":
                current_text_content = self.eve_reply_text.get("1.0", tk.END).strip()
                placeholder_text = iq_config.get("placeholder", "")
                if placeholder_text and current_text_content == placeholder_text:
                    self.eve_reply_text.delete("1.0", tk.END)
                    if hasattr(self.eve_reply_text, 'tag_remove'): # Ensure tag_remove exists
                         self.eve_reply_text.tag_remove("placeholder_italic", "1.0", tk.END) # Corrected END usage

        # Determine reply_val_store and display_reply_bubble based on context and mcq_choice
        if mcq_choice is not None: # Handles MCQ, TF, and template button clicks for select type fields
            reply_val_store = mcq_choice
            display_reply_bubble = mcq_choice
            if context.get("type") == "direct":
                field_def = context.get("field_def", {})
                if field_def.get("type") == "select": # This is for protocol's own select (dropdown)
                    # For protocol selects, mcq_choice would be the display text from a button (less likely now with combobox)
                    # Or, if we adapt MCQ buttons for protocol selects.
                    # Here, assume mcq_choice *is* the value if this path is taken for a select.
                    # For safety, ensure it's one of the valid values.
                    options_list = field_def.get("options", [])
                    # This part might need more refinement if MCQ buttons are truly used for protocol 'select'
                    # but with eve_reply_combobox, this direct mcq_choice for 'select' fields is less likely.
                    # For now, we assume if mcq_choice comes for a select, it's the *value*.
                    pass # reply_val_store is already mcq_choice
        
        elif context.get("type") == "direct":
            field_def = context.get("field_def", {})
            field_type = field_def.get("type")

            if field_type == "textarea":
                reply_val_store = self.eve_reply_text.get("1.0", tk.END).strip()
                source_widget = self.eve_reply_text
            elif field_type == "select": # Protocol's own select fields (using self.eve_reply_combobox)
                display_text_selected = self.eve_reply_select_var.get()
                reply_val_store = display_text_selected # Default to display text if no mapping
                for opt_cfg in field_def.get("options", []):
                    if opt_cfg.get("text") == display_text_selected:
                        reply_val_store = opt_cfg.get("value", display_text_selected)
                        break
                source_widget = self.eve_reply_combobox
            else: # text type for protocol field
                reply_val_store = self.eve_reply_entry.get().strip()
                source_widget = self.eve_reply_entry
            
            display_reply_bubble = reply_val_store
            if field_type == "select": # For display, always use the selected text from combobox
                display_reply_bubble = self.eve_reply_select_var.get()

        elif context.get("type") == "invented": # For invented text/textarea questions
            iq_config = context.get("iq_config", {})
            iq_type = iq_config.get("type")
            if iq_type == "textarea":
                reply_val_store = self.eve_reply_text.get("1.0", tk.END).strip()
                source_widget = self.eve_reply_text
            elif iq_type == "text":
                reply_val_store = self.eve_reply_entry.get().strip()
                source_widget = self.eve_reply_entry
            # MCQ/TF for invented are handled if mcq_choice is not None (top of function)
            display_reply_bubble = reply_val_store
        
        # --- Now, save the data and proceed ---
        # This 'if' condition checks if there's actually something to process and speak about
        data_to_log = (reply_val_store or (mcq_choice is not None) or 
                      (context.get("type") == "direct" and context.get("field_def", {}).get("type") == "select" and self.eve_reply_select_var.get()))

        if data_to_log:
            self._eve_speak(f"أنت: {display_reply_bubble}", is_user=True)
            data_updated_by_this_reply = False # Flag to track if actual data changed

            if context.get("type") == "direct":
                # ... (Logic to save to self.loaded_ucp_data for direct questions) ...
                # This part needs to be robust to missing keys/items.
                section_key = context.get("section_key")
                field_def = context.get("field_def",{})
                json_key = field_def.get("jsonKey")
                item_idx = context.get("item_index", 0)

                if section_key and json_key is not None : # item_idx can be 0
                    sections_list = self.loaded_ucp_data.setdefault("sections", [])
                    target_section_data = next((s for s in sections_list if s.get("id") == section_key), None)
                    
                    if not target_section_data: # If section doesn't exist, create it
                        target_section_data = {"id": section_key, "title": SECTION_TYPE_DATA.get(section_key,{}).get("title","Unknown Section"), "items": []}
                        sections_list.append(target_section_data)

                    items_list = target_section_data.setdefault("items", [])
                    while len(items_list) <= item_idx: # Ensure item at item_idx exists
                        items_list.append({})
                    
                    if not isinstance(items_list[item_idx], dict): # Ensure item is a dict
                        items_list[item_idx] = {}

                    if items_list[item_idx].get(json_key) != reply_val_store:
                        items_list[item_idx][json_key] = reply_val_store
                        data_updated_by_this_reply = True
                    
                    if json_key == "preferredName" and section_key == "personal":
                        self.eve_preferred_name_cache = reply_val_store or "صديقي"
                        if not data_updated_by_this_reply and (items_list[item_idx].get(json_key) != reply_val_store) : # ensure change flag if name changes
                             data_updated_by_this_reply = True


            elif context.get("type") == "invented":
                # ... (Logic to save to additional_notes for invented questions) ...
                # This also needs to be robust.
                notes_section_id = "additional_notes"
                notes_section_def = SECTION_TYPE_DATA.get(notes_section_id)
                if notes_section_def and notes_section_def.get("fields"):
                    notes_json_key = notes_section_def["fields"][0].get("jsonKey")
                    
                    sections_list = self.loaded_ucp_data.setdefault("sections", [])
                    notes_section_data = next((s for s in sections_list if s.get("id") == notes_section_id), None)

                    if not notes_section_data:
                        notes_section_data = {"id": notes_section_id, "title": notes_section_def.get("title", "ملاحظات إضافية"), "items": [{notes_json_key: ""}]}
                        sections_list.append(notes_section_data)
                    elif not notes_section_data.get("items") or not isinstance(notes_section_data.get("items"), list) or not notes_section_data["items"] or not isinstance(notes_section_data["items"][0], dict):
                        notes_section_data["items"] = [{notes_json_key: ""}] # Ensure item[0] exists and is a dict

                    current_notes = notes_section_data["items"][0].get(notes_json_key, "")
                    iq_config = context.get("iq_config", {})
                    original_iq_question = iq_config.get("question", "سؤال غير معروف")
                    
                    # Consistent quote normalization for saving IQ
                    normalized_iq_question_for_saving = original_iq_question.replace('"', "'")
                    
                    eve_note_entry = f"Eve 🧚 (Q: \"{normalized_iq_question_for_saving}\"):\nYour Answer: {reply_val_store}\n-----\n"
                    
                    new_notes_content = current_notes
                    if current_notes and current_notes.strip() and not current_notes.strip().endswith("-----"):
                        new_notes_content += "\n\n" # Add separator if notes are not empty and don't end with separator
                    new_notes_content += eve_note_entry.strip() # Add new entry, stripping its trailing newline for now

                    if notes_section_data["items"][0].get(notes_json_key) != new_notes_content:
                        notes_section_data["items"][0][notes_json_key] = new_notes_content
                        data_updated_by_this_reply = True
                else:
                    self._eve_speak("خطأ في الإعداد: قسم 'الملاحظات الإضافية' لأسئلة إيفي غير مهيأ بشكل صحيح.", is_system=True)

            if data_updated_by_this_reply:
                self._set_data_changed(True) # Mark protocol as changed
        else:
            self._eve_speak("(تخطيت أو أرسلت رداً فارغاً.)", is_user=True)

        # Clear the input widget from which the reply was taken
        if source_widget:
            if isinstance(source_widget, tk.Text):
                source_widget.delete("1.0", tk.END)
            elif isinstance(source_widget, ttk.Entry):
                source_widget.delete(0, tk.END)
            # For ttk.Combobox (protocol select), it's handled by eve_reply_select_var.set("") in _eve_show_input_type
        
        # Advance to next question
        if context.get("type") == "direct":
            self.eve_state["current_field_index"] += 1
        
        # Call ask_next_eve_question to determine the next step
        # This will handle moving to next field, next section, summaries, IQs, or API analysis choice
        self.master.after(100, self.ask_next_eve_question)
    def trigger_external_analysis(self):
        if not self.loaded_ucp_data: self._eve_speak("لا يوجد بروتوكول لتحليله.", is_system=True); self.eve_state["current_mode"] = "SESSION_COMPLETE"; self.ask_next_eve_question(); return
        if not self.groq_api_key_cache or self.groq_api_key_cache == "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx": # REPLACE placeholder too
            self._eve_speak("لم يتم إعداد مفتاح Groq API. لا يمكن إجراء التحليل.", is_system=True); messagebox.showwarning("مفتاح API غير موجود", "يرجى إعداد مفتاح Groq API."); self.eve_state["current_mode"] = "SESSION_COMPLETE"; self.ask_next_eve_question(); return
        self._eve_speak("جاري إعداد البيانات وإرسالها للتحليل الخارجي... قد يستغرق هذا بعض الوقت.", is_system=True)
        self.eve_current_question_label.config(text="⏳ جاري تحليل البروتوكول بواسطة Groq API...")
        self.eve_state["is_waiting_for_api_response"] = True; self._eve_manage_input_visibility(show_send=False, show_skip=False)
        full_protocol_text = self._generate_protocol_text_content(for_preview=False)
        analysis_prompt_template_v2 = """
<<< بداية الموجه إلى النموذج اللغوي الكبير الخارجي (النسخة المحسنة v2) >>>
أنت نموذج لغوي كبير ومحلل بيانات متخصص في فهم وتحليل الشخصيات والأنماط السلوكية والفكرية، مع التركيز على الاستنتاج المبني على الأدلة، التفكير النقدي، واستيعاب السياقات المعقدة والمتعددة الطبقات. مهمتك ليست مجرد تلخيص المعلومات، بل تقديم تحليل عميق ورؤى استنتاجية.
مهمتك هي تحليل "بروتوكول السياق الشخصي (UCP-LLM)" التالي للمستخدم، والذي تم جمعه عبر أداة متخصصة مصممة لاستخلاص معلومات عميقة ومتنوعة. هذا البروتوكول يتضمن معلومات مفصلة قدمها المستخدم عن نفسه، منظوره للعالم، قيمه، أهدافه، بالإضافة إلى إجاباته على مجموعة واسعة من الأسئلة الإبداعية والاستفهامية.
البروتوكول نفسه (كما هو مرفق أدناه) يحتوي على "مقدمة (Preamble)" و "خاتمة (Postamble)" توجهان النموذج اللغوي (مثلك) حول كيفية تفسير البيانات والبروتوكول بشكل عام، بالإضافة إلى الآليات التي يفضل المستخدم أن يتفاعل بها النموذج معه. يرجى أخذ هذه التوجيهات الهيكلية بعين الاعتبار كأساس لفهمك لدور هذا البروتوكول في توجيه تفاعلات النماذج اللغوية مع المستخدم.
**البيانات التي ستقوم بتحليلها هي كل ما يرد بعد هذا الموجه وحتى نهاية نص البروتوكول المرفق.**
**المطلوب منك:**
1.  **القراءة والفهم النقدي والتحليلي (Critical and Analytical Comprehension):**
    *   قم بقراءة وفهم البروتوكول المرفق بالكامل بعناية فائقة وتأمل. هذا يشمل جميع الأقسام الـ 25 التي يقدم فيها المستخدم بيانات منظمة عن نفسه، بالإضافة إلى قسم "الملاحظات الإضافية" (الذي قد يتضمن تحليلاً ذاتيًا من المستخدم نفسه و/أو إجابات المستخدم على أسئلة "إيفي" الإبداعية).
    *   **مهمتك ليست فقط استخلاص المعلومات، بل البحث عن الروابط، الأنماط، التناقضات المحتملة، والتجليات المتعددة للمبادئ أو القيم الأساسية للمستخدم عبر مختلف أجزاء البروتوكول.**
2.  **تقديم "ملخص تحليلي شامل لشخصية المستخدم، أنماطه الفكرية، وقيمه الأساسية":**
    *   **الهدف:** إنشاء تحليل استنتاجي عميق، غني بالرؤى، موضوعي، ومبني على الأدلة القوية من النص. يجب أن يتجاوز الملخص مجرد إعادة صياغة البيانات.
    *   **الطول المقترح:** حوالي 700 إلى 1000 كلمة، لضمان عمق التحليل.
    *   **الهيكل المقترح للملخص التحليلي (مع التركيز على التحليل وليس فقط السرد):**
        *   أ. المقدمة التحليلية (موجزة جداً)
        *   ب. الهوية المتكاملة: ربط الشخصية، الاجتماعية، التعليمية، والمهنية
        *   ج. النواة الفكرية والمنهجية (تحليل معمق)
        *   د. منظومة القيم والمبادئ الأخلاقية (تحليل تطبيقي)
        *   هـ. المنظور تجاه المفاهيم الجوهرية (تحليل مقارن)
        *   و. الأدوات المعرفية، النماذج الملهمة، والمحاذير الفكرية (تحليل وظيفي)
        *   ز. المشاريع والأهداف الحالية (تحليل الدوافع والتوجهات)
        *   ح. أسلوب التفاعل وتفضيلات النموذج (تحليل متطلبات الشراكة)
        *   ط. تحليل معمق للأنماط السلوكية والفكرية من إجابات "أسئلة إيفي الإبداعية" (جزء حيوي - ابحث عن نمط "Eve 🧚 (Q: ... Your Answer: ...") في "الملاحظات الإضافية". ادعم كل نمط بـ 2-3 أمثلة مقتبسة.)
        *   ي. محاولة تحليل الشخصية وفقًا لنموذج العوامل الخمسة الكبرى (Big Five Personality Traits) - إذا كانت البيانات تدعم ذلك (ادعم بقوة بالأدلة).
        *   ك. نقاط القوة المحورية (تحليل استنتاجي)
        *   ل. مجالات محتملة للنمو أو التأمل الذاتي (بحذر شديد، وبناءً على إشارات المستخدم فقط).
        *   م. خلاصة تحليلية شاملة وموجزة.
3.  **الأسلوب المطلوب في الملخص التحليلي:**
    *   التحليل النقدي والاستنتاجي. الموضوعية والدعم بالأدلة. الاحترام والتقدير. الوضوح واللغة الاحترافية. التكامل والربط. تجنب الافتراضات غير المبررة.
**البيانات المرفقة لتحليلها هي التالية:**
"""
        full_request_content = analysis_prompt_template_v2.strip() + "\n\n" + full_protocol_text
        api_thread = threading.Thread(target=self._send_request_to_groq_api_threaded, args=(full_request_content,), daemon=True); api_thread.start()

    def _send_request_to_groq_api_threaded(self, request_content: str):
        try:
            client = Groq(api_key=self.groq_api_key_cache)
            chat_completion = client.chat.completions.create(
                messages=[ {"role": "system", "content": "أنت محلل بيانات متخصص. اتبع التعليمات بدقة."}, {"role": "user", "content": request_content} ],
                model=self.groq_model_name_cache, temperature=0.3, max_tokens=3000 # Increased max_tokens for detailed analysis
            )
            result = chat_completion.choices[0].message.content
            self.api_result_queue.put({"status": "success", "data": result})
        except RateLimitError as e: print(f"Groq API Rate Limit Error: {e}"); self.api_result_queue.put({"status": "error", "data": f"خطأ في حدود استخدام Groq API: {e.status_code}\n{e.message}"})
        except APIError as e: print(f"Groq API Error: {e}"); self.api_result_queue.put({"status": "error", "data": f"خطأ من Groq API: {e.status_code}\n{e.message}"})
        except Exception as e: print(f"Unexpected error during Groq API call: {e}"); self.api_result_queue.put({"status": "error", "data": f"خطأ غير متوقع: {type(e).__name__} - {e}"})

    def _check_api_queue(self):
        try:
            result = self.api_result_queue.get_nowait()
            self.eve_state["is_waiting_for_api_response"] = False
            if result["status"] == "success":
                self.eve_state["api_analysis_result"] = result["data"]
                self._eve_speak("لقد عاد التحليل من النموذج اللغوي الخارجي (Groq). إليك الملخص:", is_system=True)
                self.eve_current_question_label.config(text="نتيجة التحليل من Groq:")
                self._eve_manage_input_visibility(show_send=False, show_skip=False, show_analysis_display=True, show_analysis_confirm_buttons=True)
                self.eve_state["current_mode"] = "AWAITING_API_ANALYSIS_SAVE_CHOICE"
            else:
                error_message = result["data"]; self._eve_speak(f"عذرًا، حدث خطأ أثناء التحليل الخارجي: {error_message}", is_system=True)
                self.eve_current_question_label.config(text="فشل التحليل الخارجي."); self._eve_manage_input_visibility(show_send=False, show_skip=False); self.eve_state["current_mode"] = "SESSION_COMPLETE"
        except queue.Empty: pass
        finally:
            if self.master.winfo_exists(): self.master.after(200, self._check_api_queue)

    def _save_external_analysis_to_protocol(self, analysis_text: str):
        if not self.loaded_ucp_data: return
        notes_id="additional_notes"; notes_sec_data = next((s for s in self.loaded_ucp_data.get("sections", []) if s.get("id") == notes_id), None)
        if not notes_sec_data: notes_sec_data = {"id": notes_id, "title": SECTION_TYPE_DATA[notes_id]["title"], "items": [{}]}; self.loaded_ucp_data.setdefault("sections", []).append(notes_sec_data)
        elif not notes_sec_data.get("items") or not isinstance(notes_sec_data.get("items"),list) or not notes_sec_data.get("items"): notes_sec_data["items"] = [{}]
        elif not isinstance(notes_sec_data.get("items")[0], dict): notes_sec_data["items"][0] = {}
        if not notes_sec_data.get("items"): notes_sec_data["items"] = [{}] # Final safety for item[0]
        if not isinstance(notes_sec_data.get("items")[0],dict): notes_sec_data["items"][0] = {} # If it was bad
        notes_sec_data["items"][0]["externalAnalysisSummary"] = analysis_text.strip()
        if "additionalGeneralNotes" not in notes_sec_data["items"][0]: notes_sec_data["items"][0]["additionalGeneralNotes"] = "" # Ensure field for IQs exists
        self._set_data_changed(True)

    def skip_eve_question(self):
        context = self.eve_state["current_question_context"]; self._eve_speak("(تخطيت السؤال.)", is_user=True)
        if context and context["type"] == "direct": self.eve_state["current_field_index"] += 1
        if self.eve_state["is_asking_to_add_another"]: self.eve_state["is_asking_to_add_another"]=False; self.move_to_next_eve_direct_section_or_invented(); return
        self.ask_next_eve_question()

    def prompt_edit_specific_section(self):
        if not self.loaded_ucp_data: messagebox.showinfo("لا يوجد بروتوكول", "قم بتحميل أو بدء بروتوكول أولاً."); return
        dialog = tk.Toplevel(self.master); dialog.title("✏️ تعديل قسم محدد"); dialog.transient(self.master); dialog.grab_set(); dialog.resizable(False,False)
        df = ttk.Frame(dialog, padding=20, style="EvePanel.TFrame"); df.pack(fill=tk.BOTH,expand=True)
        ttk.Label(df,text="اختر القسم الذي تود تعديله:", font=("Segoe UI",11)).pack(pady=(0,10))
        titles = [SECTION_TYPE_DATA[k]["title"] for k in self.eve_state["section_keys_order"] if k in SECTION_TYPE_DATA] # defensive check
        if not hasattr(self,'edit_section_var'): self.edit_section_var=tk.StringVar()
        cb = ttk.Combobox(df,textvariable=self.edit_section_var,values=titles,state="readonly",width=45,font=("Segoe UI",10))
        if titles: curr_key = self.get_current_eve_section_key(); self.edit_section_var.set(SECTION_TYPE_DATA[curr_key]["title"] if curr_key and curr_key in SECTION_TYPE_DATA and SECTION_TYPE_DATA[curr_key]["title"] in titles else titles[0])
        cb.pack(pady=5); bf = ttk.Frame(df, style="EvePanel.TFrame"); bf.pack(pady=15)
        def on_edit():
            sel_title = self.edit_section_var.get(); key = next((k for k,v in SECTION_TYPE_DATA.items() if v["title"]==sel_title),None)
            if key: dialog.destroy(); self._jump_to_eve_section(key)
            else: messagebox.showerror("خطأ","لم يتم العثور على مفتاح القسم.",parent=dialog)
        edit_btn = ttk.Button(bf,text="تعديل",command=on_edit,style="Eve.TButton"); edit_btn.pack(side=tk.LEFT,padx=10); Tooltip(edit_btn,"تعديل القسم المختار.")
        ttk.Button(bf,text="إلغاء",command=dialog.destroy).pack(side=tk.LEFT,padx=10); self.center_window(dialog,450,200)

    def _jump_to_eve_section(self, section_key: str):
        if section_key not in self.eve_state["section_keys_order"]: self._eve_speak(f"لا يمكن العثور على القسم: {section_key}",is_system=True); self.start_eve_interaction(); return
        target_idx = self.eve_state["section_keys_order"].index(section_key)
        if not self.loaded_ucp_data: self.loaded_ucp_data={"protocolVersion":f"{APP_VERSION} (New)","generationDate":datetime.datetime.now(UTC).isoformat(),"sections":[]}; self._set_data_changed(True); self.eve_preferred_name_cache="صديقي"
        self.eve_state.update({"current_mode":"PROCESSING_PROTOCOL", "current_section_key_index":target_idx, "current_field_index":0, "current_item_count_for_section":0, "is_asking_to_add_another":False, "initial_data_loaded_for_eve":True, "is_editing_specific_section_now":True, "is_asking_mental_state": False, "last_summary_point_triggered": "summary_3", "is_waiting_for_api_response": False}) # Set last_summary_point_triggered to prevent immediate re-trigger for that section
        self._eve_manage_input_visibility(show_send=False,show_skip=False); [w.destroy() for w in self.eve_mcq_options_frame.winfo_children()]
        self._clear_eve_conversation(); self._update_current_mental_state_cache_from_data()
        adaptive_greeting_list = EVE_MENTAL_STATE_PHRASES.get(self.current_mental_state_cache,EVE_MENTAL_STATE_PHRASES["not_specified"])["greetings"]
        adaptive_greeting = random.choice(adaptive_greeting_list).format(name=self.eve_preferred_name_cache)
        self._eve_speak(f"{adaptive_greeting} لنراجع/نعدل قسم '{SECTION_TYPE_DATA[section_key]['title']}'."); self.ask_next_eve_question()

    def _on_closing(self):
        if self.eve_state.get("is_waiting_for_api_response"):
            if not messagebox.askyesno("تحذير", "يوجد تحليل قيد المعالجة. هل أنت متأكد من الإغلاق؟", icon=messagebox.WARNING, parent=self.master): return
        if self.data_changed_since_last_save:
            res = messagebox.askyesnocancel("إغلاق","تغييرات غير محفوظة. هل تريد الحفظ قبل الإغلاق؟",parent=self.master,icon=messagebox.WARNING)
            if res is True: self.save_ucp_file_as_json(); [self.master.destroy() for _ in [] if not self.data_changed_since_last_save]
            elif res is False: self.master.destroy()
        else: self.master.destroy()

    def show_help_dialog(self):
        help_text = f"**مدير بروتوكول UCP-LLM - دليل المستخدم ({APP_VERSION})**\n\nإيفي 🧚 دليلك.\n\n**التفاعل:**\n1. ابدأ/حمّل بروتوكول.\n2. حدد حالتك الذهنية.\n3. أجب عن الأسئلة. استخدم القوالب.\n4. تقدم إيفي ملخصات دورية. أكدها أو عدّل الأقسام.\n5. **التحليل التلقائي:** في نهاية جمع البيانات، يمكنك الطلب من إيفي إرسال بروتوكولك إلى Groq API للتحليل.\n   (ملاحظة: يتطلب مفتاح Groq API صالح).\n6. احفظ/صدر البروتوكول.\n\nاستمتع!"
        self._show_info_dialog("دليل المستخدم 🧚",help_text,width=700,height=500)

    def show_about_dialog(self):
        about_text = f"**{APP_VERSION}**\n© 2024 سامح يس. جميع الحقوق محفوظة.\n\n**الجديد ({APP_VERSION.split('(')[0].split('v')[-1].strip()}):**\n* تكامل مع Groq API للتحليل التلقائي.\n* إدراج نصوص Preamble/Postamble.\n* تكيف إيفي مع الحالة الذهنية.\n* ملخصات دورية، تعديل أقسام.\n\nشكرًا!"
        self._show_info_dialog(f"عن {APP_VERSION}",about_text,width=600,height=450)

    def _show_info_dialog(self, title, text_content, width=500, height=400):
        dialog = tk.Toplevel(self.master); dialog.title(title); dialog.transient(self.master); dialog.grab_set(); dialog.resizable(True,True); mf = ttk.Frame(dialog,padding=15,style="EvePanel.TFrame"); mf.pack(fill=tk.BOTH,expand=True); ta = scrolledtext.ScrolledText(mf,wrap=tk.WORD,font=("Segoe UI",10),relief="solid",borderwidth=1,bg="white",padx=10,pady=10); ta.pack(fill=tk.BOTH,expand=True,pady=(0,10)); ta.insert(tk.END,text_content); ta.tag_configure("bold_display",font=("Segoe UI",10,"bold")); s_idx="1.0"
        while True:
            ms = ta.search(r"\*\*",s_idx,tk.END,regexp=True);
            if not ms: break
            cs_idx=f"{ms}+2c"; me=ta.search(r"\*\*",cs_idx,tk.END,regexp=True)
            if not me: break
            ta.tag_add("bold_display",cs_idx,me); s_idx=f"{me}+2c"
        ta.config(state=tk.DISABLED); ttk.Button(mf,text="إغلاق",command=dialog.destroy,style="Eve.TButton").pack(pady=(5,0)); self.center_window(dialog,width,height)

class Tooltip:
    def __init__(self,widget,text):self.w=widget;self.t=text;self.tw=None;widget.bind("<Enter>",self.s);widget.bind("<Leave>",self.h)
    def s(self,e=None): # Corrected version
        if not self.t or self.tw: return
        self.tw=tk.Toplevel(self.w); self.tw.wm_overrideredirect(True); self.tw.wm_geometry("+5000+5000")
        lbl=tk.Label(self.tw,text=self.t,justify='left',bg="#ffffe0",relief='solid',bd=1,font=("Segoe UI",9),wraplength=300); lbl.pack(ipadx=2,ipady=2)
        self.w.update_idletasks(); self.tw.update_idletasks()
        tipw=self.tw.winfo_width(); tiph=self.tw.winfo_height(); fx, fy = 0, 0 # Initialize
        try: wx=self.w.winfo_rootx(); wy=self.w.winfo_rooty(); wh=self.w.winfo_height(); ww=self.w.winfo_width(); fx=wx + (ww//2) - (tipw//2); fy=wy+wh+3
        except tk.TclError: fx=self.w.winfo_pointerx()+15; fy=self.w.winfo_pointery()+10
        scrw=self.w.winfo_screenwidth(); scrh=self.w.winfo_screenheight()
        if fx+tipw > scrw: fx=scrw-tipw-5
        if fx < 0: fx=5
        if fy+tiph > scrh: fy = (self.w.winfo_rooty() if 'wy' in locals() else self.w.winfo_pointery()) - tiph - 5
        if fy < 0: fy=5
        self.tw.wm_geometry(f"+{int(fx)}+{int(fy)}"); self.tw.deiconify()
    def h(self,e=None):
        if self.tw: self.tw.destroy(); self.tw=None

def main():
    root = tk.Tk()
    app = UCPManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
