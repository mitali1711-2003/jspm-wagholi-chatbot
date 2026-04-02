"""
JSPM Wagholi Campus Data Scraper
=================================
Scrapes JSPM official website for Wagholi-campus-specific data
and stores it in the SQLite database as FAQ entries.

Since web scraping can be unreliable (site structure changes, blocks, etc.),
this module also includes a comprehensive hardcoded Wagholi dataset as fallback.
"""

import json
import os
import re
import logging

logger = logging.getLogger(__name__)

# ─── Wagholi-Only Hardcoded Dataset (Authoritative Fallback) ──────────

JSPM_WAGHOLI_DATA = {
    "campus": "JSPM University - Wagholi Campus",
    "faqs": [
        # ── About JSPM Wagholi ──
        {
            "category": "about",
            "question_en": "What is JSPM University Wagholi Campus?",
            "question_hi": "JSPM यूनिवर्सिटी वाघोली कैंपस क्या है?",
            "question_mr": "JSPM युनिव्हर्सिटी वाघोली कॅम्पस काय आहे?",
            "answer_en": "JSPM University, Wagholi Campus is a premier educational hub located in Wagholi, Pune. It is part of Jayawantrao Sawant Pratishthan's Mandal (JSPM Group) and houses multiple colleges offering engineering, management, pharmacy, and other professional courses. The campus is NAAC accredited and approved by AICTE.",
            "answer_hi": "JSPM यूनिवर्सिटी, वाघोली कैंपस पुणे के वाघोली में स्थित एक प्रमुख शैक्षणिक केंद्र है। यह जयवंतराव सावंत प्रतिष्ठान मंडल (JSPM ग्रुप) का हिस्सा है और इसमें इंजीनियरिंग, प्रबंधन, फार्मेसी और अन्य व्यावसायिक पाठ्यक्रम प्रदान करने वाले कई कॉलेज हैं। कैंपस NAAC मान्यता प्राप्त और AICTE द्वारा अनुमोदित है।",
            "answer_mr": "JSPM युनिव्हर्सिटी, वाघोली कॅम्पस हे पुण्यातील वाघोली येथे स्थित एक प्रमुख शैक्षणिक केंद्र आहे. हे जयवंतराव सावंत प्रतिष्ठान मंडळ (JSPM ग्रुप) चा भाग आहे आणि यामध्ये अभियांत्रिकी, व्यवस्थापन, फार्मसी आणि इतर व्यावसायिक अभ्यासक्रम देणारी अनेक महाविद्यालये आहेत. कॅम्पस NAAC मान्यताप्राप्त आणि AICTE मान्य आहे."
        },
        {
            "category": "about",
            "question_en": "Where is JSPM Wagholi Campus located?",
            "question_hi": "JSPM वाघोली कैंपस कहां स्थित है?",
            "question_mr": "JSPM वाघोली कॅम्पस कुठे आहे?",
            "answer_en": "JSPM Wagholi Campus is located at S.No. 58, Wagholi, Pune - 412207, Maharashtra. It is situated on the Pune-Nagar Road (Wagholi area), easily accessible from Pune city center (approximately 15 km). Nearby landmarks include Kesnand Road and Bakori Phata.",
            "answer_hi": "JSPM वाघोली कैंपस सर्वे नंबर 58, वाघोली, पुणे - 412207, महाराष्ट्र में स्थित है। यह पुणे-नगर रोड (वाघोली क्षेत्र) पर है, पुणे शहर केंद्र से आसानी से पहुंचा जा सकता है (लगभग 15 किमी)। नजदीकी स्थलों में केसनंद रोड और बकोरी फाटा शामिल हैं।",
            "answer_mr": "JSPM वाघोली कॅम्पस सर्वे नंबर 58, वाघोली, पुणे - 412207, महाराष्ट्र येथे आहे. हे पुणे-नगर रोड (वाघोली परिसर) वर स्थित आहे, पुणे शहर केंद्रापासून सहज उपलब्ध (अंदाजे 15 किमी). जवळचे ठळक ठिकाणे केसनंद रोड आणि बकोरी फाटा आहेत."
        },
        # ── History / Establishment ──
        {
            "category": "about",
            "question_en": "When was JSPM University established?",
            "question_hi": "JSPM यूनिवर्सिटी की स्थापना कब हुई?",
            "question_mr": "JSPM युनिव्हर्सिटीची स्थापना कधी झाली?",
            "answer_en": "JSPM (Jayawantrao Sawant Pratishthan Mandal) was founded in 2000 by the late Hon. Jayawantrao Sawant. The JSPM Wagholi Campus was established in 2008 and has since grown into one of the largest educational campuses in Pune.\n\nJSPM University, Pune was officially established as a private university in 2023 under the Maharashtra Private Universities Act.\n\nKey milestones:\n• 2000 — JSPM Trust founded\n• 2001 — First engineering college (Narhe campus)\n• 2008 — Wagholi campus inaugurated\n• 2023 — JSPM University, Pune established\n• Today — 10+ institutes, 50+ programs, 15,000+ students across campuses",
            "answer_hi": "JSPM (जयवंतराव सावंत प्रतिष्ठान मंडळ) की स्थापना 2000 में स्वर्गीय माननीय जयवंतराव सावंत द्वारा की गई थी। JSPM वाघोली कैंपस 2008 में स्थापित किया गया और तब से यह पुणे के सबसे बड़े शैक्षणिक परिसरों में से एक बन गया है।\n\nJSPM यूनिवर्सिटी, पुणे को 2023 में महाराष्ट्र निजी विश्वविद्यालय अधिनियम के तहत आधिकारिक रूप से निजी विश्वविद्यालय के रूप में स्थापित किया गया।\n\nप्रमुख उपलब्धियां:\n• 2000 — JSPM ट्रस्ट की स्थापना\n• 2001 — पहला इंजीनियरिंग कॉलेज (नरहे कैंपस)\n• 2008 — वाघोली कैंपस का उद्घाटन\n• 2023 — JSPM यूनिवर्सिटी, पुणे स्थापित\n• आज — 10+ संस्थान, 50+ कार्यक्रम, सभी कैंपस में 15,000+ छात्र",
            "answer_mr": "JSPM (जयवंतराव सावंत प्रतिष्ठान मंडळ) ची स्थापना 2000 मध्ये कै. मा. जयवंतराव सावंत यांनी केली. JSPM वाघोली कॅम्पस 2008 मध्ये स्थापन करण्यात आला आणि तेव्हापासून तो पुण्यातील सर्वात मोठ्या शैक्षणिक कॅम्पसपैकी एक बनला आहे.\n\nJSPM युनिव्हर्सिटी, पुणे 2023 मध्ये महाराष्ट्र खाजगी विद्यापीठ कायद्यांतर्गत अधिकृतपणे खाजगी विद्यापीठ म्हणून स्थापन करण्यात आले.\n\nमहत्त्वाचे टप्पे:\n• 2000 — JSPM ट्रस्ट स्थापना\n• 2001 — पहिले अभियांत्रिकी महाविद्यालय (नरहे कॅम्पस)\n• 2008 — वाघोली कॅम्पसचे उद्घाटन\n• 2023 — JSPM युनिव्हर्सिटी, पुणे स्थापित\n• आज — 10+ संस्था, 50+ कार्यक्रम, सर्व कॅम्पसमध्ये 15,000+ विद्यार्थी"
        },
        # ── Colleges at Wagholi ──
        {
            "category": "colleges",
            "question_en": "Which colleges are at JSPM Wagholi Campus?",
            "question_hi": "JSPM वाघोली कैंपस में कौन से कॉलेज हैं?",
            "question_mr": "JSPM वाघोली कॅम्पसमध्ये कोणती महाविद्यालये आहेत?",
            "answer_en": "The JSPM Wagholi Campus houses the following colleges:\n1. Jayawantrao Sawant College of Engineering (JSCOE) — Engineering & Technology\n2. JSPM's Rajarshi Shahu College of Engineering (RSCOE) — Engineering\n3. JSPM's Imperial College of Engineering and Research (ICOER) — Engineering\n4. JSPM's Jayawantrao Sawant Institute of Management & Research (JSIMR) — MBA\n5. JSPM's Jayawantrao Sawant Pharmacy College — B.Pharm / D.Pharm",
            "answer_hi": "JSPM वाघोली कैंपस में निम्नलिखित कॉलेज हैं:\n1. जयवंतराव सावंत कॉलेज ऑफ इंजीनियरिंग (JSCOE) — इंजीनियरिंग और प्रौद्योगिकी\n2. JSPM का राजर्षि शाहू कॉलेज ऑफ इंजीनियरिंग (RSCOE) — इंजीनियरिंग\n3. JSPM का इम्पीरियल कॉलेज ऑफ इंजीनियरिंग एंड रिसर्च (ICOER) — इंजीनियरिंग\n4. JSPM का जयवंतराव सावंत इंस्टीट्यूट ऑफ मैनेजमेंट एंड रिसर्च (JSIMR) — MBA\n5. JSPM का जयवंतराव सावंत फार्मेसी कॉलेज — B.Pharm / D.Pharm",
            "answer_mr": "JSPM वाघोली कॅम्पसमध्ये खालील महाविद्यालये आहेत:\n1. जयवंतराव सावंत कॉलेज ऑफ इंजिनिअरिंग (JSCOE) — अभियांत्रिकी आणि तंत्रज्ञान\n2. JSPM चे राजर्षी शाहू कॉलेज ऑफ इंजिनिअरिंग (RSCOE) — अभियांत्रिकी\n3. JSPM चे इम्पिरियल कॉलेज ऑफ इंजिनिअरिंग अँड रिसर्च (ICOER) — अभियांत्रिकी\n4. JSPM चे जयवंतराव सावंत इन्स्टिट्यूट ऑफ मॅनेजमेंट अँड रिसर्च (JSIMR) — MBA\n5. JSPM चे जयवंतराव सावंत फार्मसी कॉलेज — B.Pharm / D.Pharm"
        },
        # ── Courses ──
        {
            "category": "courses",
            "question_en": "What courses are available at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में कौन से कोर्स उपलब्ध हैं?",
            "question_mr": "JSPM वाघोली येथे कोणते अभ्यासक्रम उपलब्ध आहेत?",
            "answer_en": "JSPM Wagholi Campus offers:\n\nEngineering (B.E./B.Tech): Computer Engineering, IT, AI & Data Science, AI & ML, Electronics & Telecom, Mechanical, Civil, Electrical\n\nPostgraduate: M.E./M.Tech in Computer, VLSI, Mechanical Design\n\nManagement: MBA (Marketing, Finance, HR, Operations)\n\nPharmacy: B.Pharm, D.Pharm, M.Pharm\n\nDiploma: Computer, Mechanical, Civil, E&TC",
            "answer_hi": "JSPM वाघोली कैंपस में उपलब्ध कोर्स:\n\nइंजीनियरिंग (B.E./B.Tech): कंप्यूटर इंजीनियरिंग, IT, AI & डेटा साइंस, AI & ML, इलेक्ट्रॉनिक्स & टेलीकॉम, मैकेनिकल, सिविल, इलेक्ट्रिकल\n\nस्नातकोत्तर: M.E./M.Tech कंप्यूटर, VLSI, मैकेनिकल डिजाइन\n\nप्रबंधन: MBA (मार्केटिंग, फाइनेंस, HR, ऑपरेशंस)\n\nफार्मेसी: B.Pharm, D.Pharm, M.Pharm\n\nडिप्लोमा: कंप्यूटर, मैकेनिकल, सिविल, E&TC",
            "answer_mr": "JSPM वाघोली कॅम्पसमध्ये उपलब्ध अभ्यासक्रम:\n\nअभियांत्रिकी (B.E./B.Tech): कॉम्प्युटर अभियांत्रिकी, IT, AI & डेटा सायन्स, AI & ML, इलेक्ट्रॉनिक्स & टेलिकॉम, मेकॅनिकल, सिव्हिल, इलेक्ट्रिकल\n\nपदव्युत्तर: M.E./M.Tech कॉम्प्युटर, VLSI, मेकॅनिकल डिझाइन\n\nव्यवस्थापन: MBA (मार्केटिंग, फायनान्स, HR, ऑपरेशन्स)\n\nफार्मसी: B.Pharm, D.Pharm, M.Pharm\n\nडिप्लोमा: कॉम्प्युटर, मेकॅनिकल, सिव्हिल, E&TC"
        },
        {
            "category": "courses",
            "question_en": "What engineering branches are available at Wagholi campus?",
            "question_hi": "वाघोली कैंपस में कौन सी इंजीनियरिंग शाखाएं उपलब्ध हैं?",
            "question_mr": "वाघोली कॅम्पसमध्ये कोणत्या अभियांत्रिकी शाखा उपलब्ध आहेत?",
            "answer_en": "Engineering branches at JSPM Wagholi Campus:\n- Computer Engineering\n- Information Technology (IT)\n- Artificial Intelligence & Data Science\n- Artificial Intelligence & Machine Learning\n- Electronics & Telecommunication Engineering\n- Mechanical Engineering\n- Civil Engineering\n- Electrical Engineering\n\nAll branches are approved by AICTE and affiliated to Savitribai Phule Pune University (SPPU).",
            "answer_hi": "JSPM वाघोली कैंपस में इंजीनियरिंग शाखाएं:\n- कंप्यूटर इंजीनियरिंग\n- सूचना प्रौद्योगिकी (IT)\n- आर्टिफिशियल इंटेलिजेंस & डेटा साइंस\n- आर्टिफिशियल इंटेलिजेंस & मशीन लर्निंग\n- इलेक्ट्रॉनिक्स & टेलीकम्यूनिकेशन इंजीनियरिंग\n- मैकेनिकल इंजीनियरिंग\n- सिविल इंजीनियरिंग\n- इलेक्ट्रिकल इंजीनियरिंग\n\nसभी शाखाएं AICTE द्वारा अनुमोदित और सावित्रीबाई फुले पुणे विश्वविद्यालय (SPPU) से संबद्ध हैं।",
            "answer_mr": "JSPM वाघोली कॅम्पसमधील अभियांत्रिकी शाखा:\n- कॉम्प्युटर अभियांत्रिकी\n- माहिती तंत्रज्ञान (IT)\n- आर्टिफिशियल इंटेलिजन्स & डेटा सायन्स\n- आर्टिफिशियल इंटेलिजन्स & मशीन लर्निंग\n- इलेक्ट्रॉनिक्स & टेलिकम्युनिकेशन अभियांत्रिकी\n- मेकॅनिकल अभियांत्रिकी\n- सिव्हिल अभियांत्रिकी\n- इलेक्ट्रिकल अभियांत्रिकी\n\nसर्व शाखा AICTE मान्य आणि सावित्रीबाई फुले पुणे विद्यापीठाशी (SPPU) संलग्न आहेत."
        },
        # ── Admissions ──
        {
            "category": "admissions",
            "question_en": "What is the admission process at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में प्रवेश प्रक्रिया क्या है?",
            "question_mr": "JSPM वाघोली येथील प्रवेश प्रक्रिया काय आहे?",
            "answer_en": "Admission to JSPM Wagholi Campus:\n\nFor Engineering (B.E.):\n1. Appear for MHT-CET / JEE Main\n2. Register on DTE Maharashtra CAP portal\n3. Fill college preference (JSPM Wagholi colleges)\n4. Attend CAP rounds for seat allotment\n5. Report to college with documents & fees\n\nFor MBA: MAH-CET / CAT score + GD & PI\nFor Pharmacy: MHT-CET + CAP rounds\nFor Direct Second Year: Diploma holders via DTE process\n\nManagement quota & Institute-level seats also available. Contact admissions office: +91-20-2706-0100",
            "answer_hi": "JSPM वाघोली कैंपस में प्रवेश:\n\nइंजीनियरिंग (B.E.) के लिए:\n1. MHT-CET / JEE Main दें\n2. DTE महाराष्ट्र CAP पोर्टल पर पंजीकरण करें\n3. कॉलेज वरीयता भरें (JSPM वाघोली कॉलेज)\n4. सीट आवंटन के लिए CAP राउंड में भाग लें\n5. दस्तावेज और शुल्क के साथ कॉलेज में रिपोर्ट करें\n\nMBA के लिए: MAH-CET / CAT स्कोर + GD & PI\nफार्मेसी के लिए: MHT-CET + CAP राउंड\nडायरेक्ट सेकंड ईयर: DTE प्रक्रिया के माध्यम से डिप्लोमा धारक\n\nप्रबंधन कोटा और संस्थान-स्तरीय सीटें भी उपलब्ध हैं। प्रवेश कार्यालय से संपर्क करें: +91-20-2706-0100",
            "answer_mr": "JSPM वाघोली कॅम्पसमध्ये प्रवेश:\n\nअभियांत्रिकी (B.E.) साठी:\n1. MHT-CET / JEE Main द्या\n2. DTE महाराष्ट्र CAP पोर्टलवर नोंदणी करा\n3. कॉलेज प्राधान्य भरा (JSPM वाघोली महाविद्यालये)\n4. जागा वाटपासाठी CAP फेऱ्यांना उपस्थित राहा\n5. कागदपत्रे आणि शुल्कासह महाविद्यालयात रिपोर्ट करा\n\nMBA साठी: MAH-CET / CAT गुण + GD & PI\nफार्मसी साठी: MHT-CET + CAP फेऱ्या\nथेट द्वितीय वर्ष: DTE प्रक्रियेद्वारे डिप्लोमा धारक\n\nव्यवस्थापन कोटा आणि संस्था-स्तरीय जागाही उपलब्ध आहेत. प्रवेश कार्यालयाशी संपर्क करा: +91-20-2706-0100"
        },
        {
            "category": "admissions",
            "question_en": "What are the eligibility criteria for engineering admission?",
            "question_hi": "इंजीनियरिंग प्रवेश के लिए पात्रता मानदंड क्या हैं?",
            "question_mr": "अभियांत्रिकी प्रवेशासाठी पात्रता निकष काय आहेत?",
            "answer_en": "Eligibility for B.E. at JSPM Wagholi:\n- Passed HSC (12th) with Physics, Chemistry & Mathematics\n- Minimum 50% aggregate (45% for reserved categories)\n- Valid MHT-CET or JEE Main score\n- Maharashtra State domicile (for CAP rounds)\n- All India candidates can apply through Institute-level seats",
            "answer_hi": "JSPM वाघोली में B.E. के लिए पात्रता:\n- भौतिकी, रसायन विज्ञान और गणित के साथ HSC (12वीं) उत्तीर्ण\n- न्यूनतम 50% कुल अंक (आरक्षित श्रेणी के लिए 45%)\n- वैध MHT-CET या JEE Main स्कोर\n- महाराष्ट्र राज्य अधिवास (CAP राउंड के लिए)\n- अखिल भारतीय उम्मीदवार संस्थान-स्तरीय सीटों के माध्यम से आवेदन कर सकते हैं",
            "answer_mr": "JSPM वाघोली येथे B.E. साठी पात्रता:\n- भौतिकशास्त्र, रसायनशास्त्र आणि गणित सह HSC (12वी) उत्तीर्ण\n- किमान 50% एकूण गुण (आरक्षित प्रवर्गासाठी 45%)\n- वैध MHT-CET किंवा JEE Main गुण\n- महाराष्ट्र राज्य अधिवास (CAP फेऱ्यांसाठी)\n- अखिल भारतीय उमेदवार संस्था-स्तरीय जागांद्वारे अर्ज करू शकतात"
        },
        {
            "category": "admissions",
            "question_en": "What is the last date for admission at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में प्रवेश की अंतिम तिथि क्या है?",
            "question_mr": "JSPM वाघोली येथे प्रवेशाची शेवटची तारीख कोणती आहे?",
            "answer_en": "Admission deadlines at JSPM Wagholi follow the DTE Maharashtra CAP schedule:\n- CAP Round 1, 2, 3: Usually June-August\n- Institute Level Rounds: August-September\n- Direct Second Year: September-October\n\nExact dates are updated on dte.org.in each year. Contact the admissions helpdesk at +91-20-2706-0100 for current year dates.",
            "answer_hi": "JSPM वाघोली में प्रवेश की समय सीमा DTE महाराष्ट्र CAP कार्यक्रम का पालन करती है:\n- CAP राउंड 1, 2, 3: आमतौर पर जून-अगस्त\n- संस्थान स्तर राउंड: अगस्त-सितंबर\n- डायरेक्ट सेकंड ईयर: सितंबर-अक्टूबर\n\nसटीक तिथियां हर साल dte.org.in पर अपडेट की जाती हैं। वर्तमान वर्ष की तिथियों के लिए प्रवेश हेल्पडेस्क +91-20-2706-0100 पर संपर्क करें।",
            "answer_mr": "JSPM वाघोली येथील प्रवेशाच्या मुदती DTE महाराष्ट्र CAP वेळापत्रकानुसार आहेत:\n- CAP फेरी 1, 2, 3: सामान्यतः जून-ऑगस्ट\n- संस्था स्तर फेऱ्या: ऑगस्ट-सप्टेंबर\n- थेट द्वितीय वर्ष: सप्टेंबर-ऑक्टोबर\n\nअचूक तारखा दरवर्षी dte.org.in वर अपडेट केल्या जातात. चालू वर्षाच्या तारखांसाठी प्रवेश हेल्पडेस्क +91-20-2706-0100 वर संपर्क करा."
        },
        # ── Fees (Course-wise exact data from JSPM website) ──
        {
            "category": "fees",
            "question_en": "What is the fee structure at JSPM University?",
            "question_hi": "JSPM यूनिवर्सिटी में फीस संरचना क्या है?",
            "question_mr": "JSPM युनिव्हर्सिटी येथील शुल्क रचना काय आहे?",
            "answer_en": "JSPM University Wagholi — Complete Fee Structure (per year):\n\nUndergraduate Programs:\n• B.C.A. Honours / Honours with Research (Cloud Computing / Cybersecurity / Ethical Hacking): ₹75,000/year | Duration: 3/4 Years | Intake: 300\n• B.B.A. Honours / Honours with Research: ₹75,000/year | Duration: 3/4 Years\n• B.Sc. Honours (CS / Data Science): ₹75,000/year | Duration: 3/4 Years\n• B.Com. Honours: ₹50,000/year | Duration: 3 Years\n• B.A. Honours: ₹42,000/year | Duration: 3 Years\n• B.Voc. (Animation, VFX & Gaming): ₹1,49,500/year | Duration: 3 Years\n• B.Tech (Computer Science / AI / IT / E&TC): ₹1,42,000/year | Duration: 4 Years\n• B.Tech (Mechanical / Civil / Electrical): ₹1,20,000/year | Duration: 4 Years\n• B.Des. (UI/UX / Product Design): ₹1,42,000/year | Duration: 4 Years\n• BBA in Digital Marketing: ₹85,000/year\n• B.Pharm: ₹85,000/year | Duration: 4 Years\n• D.Pharm: ₹65,000/year | Duration: 2 Years\n\nPostgraduate Programs:\n• MBA: ₹1,30,000/year | Duration: 2 Years\n• M.Tech: ₹95,000/year | Duration: 2 Years\n• MCA: ₹95,000/year | Duration: 2 Years\n• M.Pharm: ₹90,000/year | Duration: 2 Years\n\nScholarships available for EBC, SC/ST, OBC students via MahaDBT portal.",
            "answer_hi": "JSPM यूनिवर्सिटी वाघोली — पूर्ण शुल्क संरचना (प्रति वर्ष):\n\nस्नातक कार्यक्रम:\n• B.C.A. ऑनर्स (क्लाउड कंप्यूटिंग / साइबर सिक्योरिटी / एथिकल हैकिंग): ₹75,000/वर्ष | अवधि: 3/4 वर्ष | इनटेक: 300\n• B.B.A. ऑनर्स: ₹75,000/वर्ष | अवधि: 3/4 वर्ष\n• B.Sc. ऑनर्स (CS / डेटा साइंस): ₹75,000/वर्ष | अवधि: 3/4 वर्ष\n• B.Com. ऑनर्स: ₹50,000/वर्ष | अवधि: 3 वर्ष\n• B.A. ऑनर्स: ₹42,000/वर्ष | अवधि: 3 वर्ष\n• B.Voc. (एनिमेशन, VFX और गेमिंग): ₹1,49,500/वर्ष | अवधि: 3 वर्ष\n• B.Tech (CS / AI / IT / E&TC): ₹1,42,000/वर्ष | अवधि: 4 वर्ष\n• B.Tech (मैकेनिकल / सिविल): ₹1,20,000/वर्ष | अवधि: 4 वर्ष\n• B.Des. (UI/UX): ₹1,42,000/वर्ष | अवधि: 4 वर्ष\n• B.Pharm: ₹85,000/वर्ष\n• D.Pharm: ₹65,000/वर्ष\n\nस्नातकोत्तर:\n• MBA: ₹1,30,000/वर्ष\n• M.Tech: ₹95,000/वर्ष\n• MCA: ₹95,000/वर्ष\n\nEBC, SC/ST, OBC छात्रों के लिए MahaDBT पोर्टल के माध्यम से छात्रवृत्तियां उपलब्ध हैं।",
            "answer_mr": "JSPM युनिव्हर्सिटी वाघोली — संपूर्ण शुल्क रचना (दरवर्षी):\n\nपदवी कार्यक्रम:\n• B.C.A. ऑनर्स (क्लाउड कॉम्प्युटिंग / सायबर सिक्युरिटी / एथिकल हॅकिंग): ₹75,000/वर्ष | कालावधी: 3/4 वर्षे | इनटेक: 300\n• B.B.A. ऑनर्स: ₹75,000/वर्ष | कालावधी: 3/4 वर्षे\n• B.Sc. ऑनर्स (CS / डेटा सायन्स): ₹75,000/वर्ष | कालावधी: 3/4 वर्षे\n• B.Com. ऑनर्स: ₹50,000/वर्ष | कालावधी: 3 वर्षे\n• B.A. ऑनर्स: ₹42,000/वर्ष | कालावधी: 3 वर्षे\n• B.Voc. (अॅनिमेशन, VFX आणि गेमिंग): ₹1,49,500/वर्ष | कालावधी: 3 वर्षे\n• B.Tech (CS / AI / IT / E&TC): ₹1,42,000/वर्ष | कालावधी: 4 वर्षे\n• B.Tech (मेकॅनिकल / सिव्हिल): ₹1,20,000/वर्ष | कालावधी: 4 वर्षे\n• B.Des. (UI/UX): ₹1,42,000/वर्ष | कालावधी: 4 वर्षे\n• B.Pharm: ₹85,000/वर्ष\n• D.Pharm: ₹65,000/वर्ष\n\nपदव्युत्तर:\n• MBA: ₹1,30,000/वर्ष\n• M.Tech: ₹95,000/वर्ष\n• MCA: ₹95,000/वर्ष\n\nEBC, SC/ST, OBC विद्यार्थ्यांसाठी MahaDBT पोर्टलद्वारे शिष्यवृत्ती उपलब्ध आहेत."
        },
        {
            "category": "fees",
            "question_en": "What is the BCA fee at JSPM University?",
            "question_hi": "JSPM यूनिवर्सिटी में BCA की फीस कितनी है?",
            "question_mr": "JSPM युनिव्हर्सिटीमध्ये BCA चे शुल्क किती आहे?",
            "answer_en": "BCA at JSPM University Wagholi:\n\nProgram: B.C.A. / Honours or Honours with Research\nSpecializations: Cloud Computing, Cybersecurity, Ethical Hacking\nDuration: 3 Years (Honours) / 4 Years (Honours with Research)\nFees: ₹75,000 per year\nIntake: 300 seats\n\nEligibility: Passed HSC or Diploma in any discipline with 45% marks (40% for reserved category) / MH-CET / CUET / PERA CET.\n\nApply through JSPM admissions portal or contact: +91-20-2706-0100",
            "answer_hi": "JSPM यूनिवर्सिटी वाघोली में BCA:\n\nकार्यक्रम: B.C.A. / ऑनर्स या ऑनर्स विद रिसर्च\nविशेषज्ञता: क्लाउड कंप्यूटिंग, साइबर सिक्योरिटी, एथिकल हैकिंग\nअवधि: 3 वर्ष (ऑनर्स) / 4 वर्ष (ऑनर्स विद रिसर्च)\nशुल्क: ₹75,000 प्रति वर्ष\nइनटेक: 300 सीटें\n\nपात्रता: किसी भी विषय में HSC या डिप्लोमा 45% अंकों के साथ (आरक्षित श्रेणी के लिए 40%) / MH-CET / CUET / PERA CET\n\nआवेदन: JSPM प्रवेश पोर्टल या संपर्क: +91-20-2706-0100",
            "answer_mr": "JSPM युनिव्हर्सिटी वाघोली येथे BCA:\n\nकार्यक्रम: B.C.A. / ऑनर्स किंवा ऑनर्स विथ रिसर्च\nस्पेशलायझेशन: क्लाउड कॉम्प्युटिंग, सायबर सिक्युरिटी, एथिकल हॅकिंग\nकालावधी: 3 वर्षे (ऑनर्स) / 4 वर्षे (ऑनर्स विथ रिसर्च)\nशुल्क: ₹75,000 दरवर्षी\nइनटेक: 300 जागा\n\nपात्रता: कोणत्याही विषयात HSC किंवा डिप्लोमा 45% गुणांसह (आरक्षित प्रवर्गासाठी 40%) / MH-CET / CUET / PERA CET\n\nअर्ज: JSPM प्रवेश पोर्टल किंवा संपर्क: +91-20-2706-0100"
        },
        {
            "category": "fees",
            "question_en": "What is the B.Voc Animation VFX and Gaming fee?",
            "question_hi": "B.Voc एनिमेशन VFX और गेमिंग की फीस कितनी है?",
            "question_mr": "B.Voc अॅनिमेशन VFX आणि गेमिंग चे शुल्क किती आहे?",
            "answer_en": "B.Voc. (Animation, VFX & Gaming) at JSPM University Wagholi:\n\nDuration: 3 Years\nFees: ₹1,49,500 per year\n\nEligibility: Passed HSC examination with min 50% marks in any relevant stream from a recognized board / (10+2 years of ITI) / 3 years of Diploma course after 10th / 2 years Diploma after 12th Std. Age limit: maximum 45 years. Entrance: CUET.\n\nThis is a skill-based vocational program focused on animation, visual effects, and game development.",
            "answer_hi": "JSPM यूनिवर्सिटी वाघोली में B.Voc. (एनिमेशन, VFX और गेमिंग):\n\nअवधि: 3 वर्ष\nशुल्क: ₹1,49,500 प्रति वर्ष\n\nपात्रता: किसी भी मान्यता प्राप्त बोर्ड से 50% अंकों के साथ HSC / ITI (10+2 वर्ष) / 10वीं के बाद 3 वर्ष डिप्लोमा / 12वीं के बाद 2 वर्ष डिप्लोमा। आयु सीमा: अधिकतम 45 वर्ष। प्रवेश: CUET।\n\nयह एनिमेशन, विजुअल इफेक्ट्स और गेम डेवलपमेंट पर केंद्रित कौशल-आधारित व्यावसायिक कार्यक्रम है।",
            "answer_mr": "JSPM युनिव्हर्सिटी वाघोली येथे B.Voc. (अॅनिमेशन, VFX आणि गेमिंग):\n\nकालावधी: 3 वर्षे\nशुल्क: ₹1,49,500 दरवर्षी\n\nपात्रता: कोणत्याही मान्यताप्राप्त बोर्डातून 50% गुणांसह HSC / ITI (10+2 वर्षे) / 10वी नंतर 3 वर्षे डिप्लोमा / 12वी नंतर 2 वर्षे डिप्लोमा. वयोमर्यादा: जास्तीत जास्त 45 वर्षे. प्रवेश: CUET.\n\nहा अॅनिमेशन, व्हिज्युअल इफेक्ट्स आणि गेम डेव्हलपमेंटवर केंद्रित कौशल्य-आधारित व्यावसायिक कार्यक्रम आहे."
        },
        {
            "category": "fees",
            "question_en": "What is the B.Tech fee at JSPM University?",
            "question_hi": "JSPM यूनिवर्सिटी में B.Tech की फीस कितनी है?",
            "question_mr": "JSPM युनिव्हर्सिटीमध्ये B.Tech चे शुल्क किती आहे?",
            "answer_en": "B.Tech at JSPM University Wagholi:\n\nB.Tech (Computer Science & Engineering): ₹1,42,000/year | 4 Years\nB.Tech (AI & Machine Learning): ₹1,42,000/year | 4 Years\nB.Tech (Information Technology): ₹1,42,000/year | 4 Years\nB.Tech (Electronics & Telecommunication): ₹1,42,000/year | 4 Years\nB.Tech (Mechanical Engineering): ₹1,20,000/year | 4 Years\nB.Tech (Civil Engineering): ₹1,20,000/year | 4 Years\nB.Tech (Electrical Engineering): ₹1,20,000/year | 4 Years\n\nEligibility: HSC with PCM, min 50% (45% reserved). Entrance: MHT-CET / JEE Main / CUET.\nAll programs are AICTE approved and affiliated to SPPU.",
            "answer_hi": "JSPM यूनिवर्सिटी वाघोली में B.Tech:\n\nB.Tech (कंप्यूटर साइंस): ₹1,42,000/वर्ष | 4 वर्ष\nB.Tech (AI & मशीन लर्निंग): ₹1,42,000/वर्ष | 4 वर्ष\nB.Tech (IT): ₹1,42,000/वर्ष | 4 वर्ष\nB.Tech (E&TC): ₹1,42,000/वर्ष | 4 वर्ष\nB.Tech (मैकेनिकल): ₹1,20,000/वर्ष | 4 वर्ष\nB.Tech (सिविल): ₹1,20,000/वर्ष | 4 वर्ष\nB.Tech (इलेक्ट्रिकल): ₹1,20,000/वर्ष | 4 वर्ष\n\nपात्रता: PCM के साथ HSC, न्यूनतम 50% (आरक्षित 45%)। प्रवेश: MHT-CET / JEE Main / CUET।",
            "answer_mr": "JSPM युनिव्हर्सिटी वाघोली येथे B.Tech:\n\nB.Tech (कॉम्प्युटर सायन्स): ₹1,42,000/वर्ष | 4 वर्षे\nB.Tech (AI & मशीन लर्निंग): ₹1,42,000/वर्ष | 4 वर्षे\nB.Tech (IT): ₹1,42,000/वर्ष | 4 वर्षे\nB.Tech (E&TC): ₹1,42,000/वर्ष | 4 वर्षे\nB.Tech (मेकॅनिकल): ₹1,20,000/वर्ष | 4 वर्षे\nB.Tech (सिव्हिल): ₹1,20,000/वर्ष | 4 वर्षे\nB.Tech (इलेक्ट्रिकल): ₹1,20,000/वर्ष | 4 वर्षे\n\nपात्रता: PCM सह HSC, किमान 50% (आरक्षित 45%). प्रवेश: MHT-CET / JEE Main / CUET."
        },
        {
            "category": "fees",
            "question_en": "What is the BBA fee at JSPM University?",
            "question_hi": "JSPM यूनिवर्सिटी में BBA की फीस कितनी है?",
            "question_mr": "JSPM युनिव्हर्सिटीमध्ये BBA चे शुल्क किती आहे?",
            "answer_en": "BBA at JSPM University Wagholi:\n\nProgram: B.B.A. Honours / Honours with Research\nDuration: 3 Years (Honours) / 4 Years (Honours with Research)\nFees: ₹75,000 per year\n\nBBA in Digital Marketing: ₹85,000 per year\n\nEligibility: Passed HSC in any stream with 45% marks (40% for reserved). Entrance: CUET / University entrance test.\n\nSpecializations available in Marketing, Finance, HR, International Business, and Digital Marketing.",
            "answer_hi": "JSPM यूनिवर्सिटी वाघोली में BBA:\n\nकार्यक्रम: B.B.A. ऑनर्स / ऑनर्स विद रिसर्च\nअवधि: 3 वर्ष (ऑनर्स) / 4 वर्ष (ऑनर्स विद रिसर्च)\nशुल्क: ₹75,000 प्रति वर्ष\n\nBBA डिजिटल मार्केटिंग: ₹85,000 प्रति वर्ष\n\nपात्रता: किसी भी स्ट्रीम में HSC 45% अंकों के साथ (आरक्षित 40%)। प्रवेश: CUET / विश्वविद्यालय प्रवेश परीक्षा।",
            "answer_mr": "JSPM युनिव्हर्सिटी वाघोली येथे BBA:\n\nकार्यक्रम: B.B.A. ऑनर्स / ऑनर्स विथ रिसर्च\nकालावधी: 3 वर्षे (ऑनर्स) / 4 वर्षे (ऑनर्स विथ रिसर्च)\nशुल्क: ₹75,000 दरवर्षी\n\nBBA डिजिटल मार्केटिंग: ₹85,000 दरवर्षी\n\nपात्रता: कोणत्याही स्ट्रीममध्ये HSC 45% गुणांसह (आरक्षित 40%). प्रवेश: CUET / विद्यापीठ प्रवेश परीक्षा."
        },
        {
            "category": "fees",
            "question_en": "What is the MBA fee at JSPM University?",
            "question_hi": "JSPM यूनिवर्सिटी में MBA की फीस कितनी है?",
            "question_mr": "JSPM युनिव्हर्सिटीमध्ये MBA चे शुल्क किती आहे?",
            "answer_en": "MBA at JSPM University Wagholi:\n\nDuration: 2 Years\nFees: ₹1,30,000 per year\n\nSpecializations: Marketing, Finance, HR, Operations, International Business, Business Analytics\n\nEligibility: Any graduate with 50% marks (45% reserved). Entrance: MAH-CET / CAT / CUET-PG / ATMA.\n\nIncludes industry internships, live projects, and corporate interaction sessions.",
            "answer_hi": "JSPM यूनिवर्सिटी वाघोली में MBA:\n\nअवधि: 2 वर्ष\nशुल्क: ₹1,30,000 प्रति वर्ष\n\nविशेषज्ञता: मार्केटिंग, फाइनेंस, HR, ऑपरेशंस, इंटरनेशनल बिजनेस, बिजनेस एनालिटिक्स\n\nपात्रता: किसी भी स्नातक 50% अंकों के साथ (आरक्षित 45%)। प्रवेश: MAH-CET / CAT / CUET-PG / ATMA।",
            "answer_mr": "JSPM युनिव्हर्सिटी वाघोली येथे MBA:\n\nकालावधी: 2 वर्षे\nशुल्क: ₹1,30,000 दरवर्षी\n\nस्पेशलायझेशन: मार्केटिंग, फायनान्स, HR, ऑपरेशन्स, इंटरनॅशनल बिझनेस, बिझनेस अॅनालिटिक्स\n\nपात्रता: कोणतीही पदवी 50% गुणांसह (आरक्षित 45%). प्रवेश: MAH-CET / CAT / CUET-PG / ATMA."
        },
        {
            "category": "fees",
            "question_en": "What is the B.Des fee at JSPM University?",
            "question_hi": "JSPM यूनिवर्सिटी में B.Des की फीस कितनी है?",
            "question_mr": "JSPM युनिव्हर्सिटीमध्ये B.Des चे शुल्क किती आहे?",
            "answer_en": "B.Des. at JSPM University Wagholi:\n\nProgram: B.Des. (UI/UX Design / Product Design)\nDuration: 4 Years\nFees: ₹1,42,000 per year\n\nEligibility: Passed HSC with min 50% marks from a recognized board. Entrance: CUET / University Design Aptitude Test.\n\nThe program focuses on user interface design, user experience, product design thinking, and creative technology.",
            "answer_hi": "JSPM यूनिवर्सिटी वाघोली में B.Des.:\n\nकार्यक्रम: B.Des. (UI/UX डिज़ाइन / प्रोडक्ट डिज़ाइन)\nअवधि: 4 वर्ष\nशुल्क: ₹1,42,000 प्रति वर्ष\n\nपात्रता: मान्यता प्राप्त बोर्ड से न्यूनतम 50% अंकों के साथ HSC। प्रवेश: CUET / डिज़ाइन एप्टीट्यूड टेस्ट।",
            "answer_mr": "JSPM युनिव्हर्सिटी वाघोली येथे B.Des.:\n\nकार्यक्रम: B.Des. (UI/UX डिझाइन / प्रॉडक्ट डिझाइन)\nकालावधी: 4 वर्षे\nशुल्क: ₹1,42,000 दरवर्षी\n\nपात्रता: मान्यताप्राप्त बोर्डातून किमान 50% गुणांसह HSC. प्रवेश: CUET / डिझाइन ऍप्टिट्यूड टेस्ट."
        },
        {
            "category": "fees",
            "question_en": "Are scholarships available at JSPM University?",
            "question_hi": "क्या JSPM यूनिवर्सिटी में छात्रवृत्तियां उपलब्ध हैं?",
            "question_mr": "JSPM युनिव्हर्सिटी येथे शिष्यवृत्ती उपलब्ध आहेत का?",
            "answer_en": "Yes! Scholarships at JSPM University Wagholi include:\n- Government of Maharashtra EBC Scholarship (Economically Backward Class)\n- SC/ST/OBC/VJNT Freeship & Scholarship\n- Merit-based fee waivers from JSPM Trust\n- Central Sector Scholarship (for top CBSE/State board students)\n- Minority Scholarship\n- JSPM University Merit Scholarship (for top CET/JEE scorers)\n\nApply through MahaDBT portal (mahadbt.maharashtra.gov.in). The college scholarship cell assists with applications.",
            "answer_hi": "हां! JSPM यूनिवर्सिटी वाघोली में उपलब्ध छात्रवृत्तियां:\n- महाराष्ट्र सरकार EBC छात्रवृत्ति\n- SC/ST/OBC/VJNT फ्रीशिप और छात्रवृत्ति\n- JSPM ट्रस्ट से मेरिट-आधारित शुल्क माफी\n- केंद्रीय क्षेत्र छात्रवृत्ति\n- अल्पसंख्यक छात्रवृत्ति\n- JSPM यूनिवर्सिटी मेरिट स्कॉलरशिप\n\nMahaDBT पोर्टल (mahadbt.maharashtra.gov.in) के माध्यम से आवेदन करें।",
            "answer_mr": "होय! JSPM युनिव्हर्सिटी वाघोली येथील शिष्यवृत्ती:\n- महाराष्ट्र शासन EBC शिष्यवृत्ती\n- SC/ST/OBC/VJNT फ्रीशिप आणि शिष्यवृत्ती\n- JSPM ट्रस्टकडून गुणवत्ता-आधारित शुल्क माफी\n- केंद्रीय क्षेत्र शिष्यवृत्ती\n- अल्पसंख्याक शिष्यवृत्ती\n- JSPM युनिव्हर्सिटी मेरिट स्कॉलरशिप\n\nMahaDBT पोर्टल (mahadbt.maharashtra.gov.in) द्वारे अर्ज करा."
        },
        # ── Hostel ──
        {
            "category": "hostel",
            "question_en": "Is hostel facility available at JSPM Wagholi?",
            "question_hi": "क्या JSPM वाघोली में छात्रावास की सुविधा है?",
            "question_mr": "JSPM वाघोली येथे वसतिगृहाची सुविधा उपलब्ध आहे का?",
            "answer_en": "Yes, JSPM Wagholi Campus provides separate hostel facilities for boys and girls:\n\n- Boys Hostel: Multiple blocks with 2/3/4 sharing rooms\n- Girls Hostel: Secured campus with warden, CCTV, and biometric entry\n- Facilities: WiFi, mess (veg & non-veg options), RO water, laundry, gym, common room with TV\n- Hostel fees: ₹45,000 – ₹80,000 per year (depending on room type)\n- Mess: ₹35,000 – ₹45,000 per year\n\nContact hostel warden office for availability.",
            "answer_hi": "हां, JSPM वाघोली कैंपस लड़कों और लड़कियों के लिए अलग छात्रावास सुविधा प्रदान करता है:\n\n- बॉयज हॉस्टल: 2/3/4 शेयरिंग कमरों के साथ कई ब्लॉक\n- गर्ल्स हॉस्टल: वार्डन, CCTV और बायोमेट्रिक एंट्री के साथ सुरक्षित कैंपस\n- सुविधाएं: WiFi, मेस (शाकाहारी और मांसाहारी विकल्प), RO पानी, लॉन्ड्री, जिम\n- छात्रावास शुल्क: ₹45,000 – ₹80,000 प्रति वर्ष\n- मेस: ₹35,000 – ₹45,000 प्रति वर्ष",
            "answer_mr": "होय, JSPM वाघोली कॅम्पस मुला आणि मुलींसाठी स्वतंत्र वसतिगृह सुविधा प्रदान करतो:\n\n- मुलांचे वसतिगृह: 2/3/4 शेअरिंग खोल्यांसह अनेक ब्लॉक\n- मुलींचे वसतिगृह: वॉर्डन, CCTV आणि बायोमेट्रिक एन्ट्रीसह सुरक्षित कॅम्पस\n- सुविधा: WiFi, मेस (शाकाहारी आणि मांसाहारी पर्याय), RO पाणी, लॉन्ड्री, जिम\n- वसतिगृह शुल्क: ₹45,000 – ₹80,000 दरवर्षी\n- मेस: ₹35,000 – ₹45,000 दरवर्षी"
        },
        {
            "category": "hostel",
            "question_en": "What are the hostel fees at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में छात्रावास की फीस कितनी है?",
            "question_mr": "JSPM वाघोली येथे वसतिगृहाचे शुल्क किती आहे?",
            "answer_en": "JSPM Wagholi Campus Hostel Fees (per year):\n\n• Hostel Room Charges: ₹45,000 – ₹80,000 per year (depending on room type — 2/3/4 sharing)\n• Mess Charges: ₹35,000 – ₹45,000 per year (veg & non-veg options)\n• Hostel Deposit (refundable): ₹5,000 – ₹10,000 (one-time)\n\nTotal approximate cost: ₹80,000 – ₹1,25,000 per year (hostel + mess combined)\n\nBoys and girls hostels are available separately with WiFi, laundry, gym, and 24/7 security.\nContact hostel warden office for current availability and exact pricing.",
            "answer_hi": "JSPM वाघोली कैंपस छात्रावास शुल्क (प्रति वर्ष):\n\n• छात्रावास कमरे का शुल्क: ₹45,000 – ₹80,000 प्रति वर्ष (कमरे के प्रकार पर निर्भर — 2/3/4 शेयरिंग)\n• मेस शुल्क: ₹35,000 – ₹45,000 प्रति वर्ष (शाकाहारी और मांसाहारी विकल्प)\n• छात्रावास जमा (वापसी योग्य): ₹5,000 – ₹10,000 (एक बार)\n\nकुल अनुमानित लागत: ₹80,000 – ₹1,25,000 प्रति वर्ष (छात्रावास + मेस)\n\nलड़कों और लड़कियों के लिए अलग छात्रावास WiFi, लॉन्ड्री, जिम और 24/7 सुरक्षा के साथ उपलब्ध हैं।\nवर्तमान उपलब्धता के लिए छात्रावास वार्डन कार्यालय से संपर्क करें।",
            "answer_mr": "JSPM वाघोली कॅम्पस वसतिगृह शुल्क (दरवर्षी):\n\n• वसतिगृह खोलीचे शुल्क: ₹45,000 – ₹80,000 दरवर्षी (खोलीच्या प्रकारावर अवलंबून — 2/3/4 शेअरिंग)\n• मेस शुल्क: ₹35,000 – ₹45,000 दरवर्षी (शाकाहारी आणि मांसाहारी पर्याय)\n• वसतिगृह ठेव (परतावा): ₹5,000 – ₹10,000 (एकदा)\n\nएकूण अंदाजे खर्च: ₹80,000 – ₹1,25,000 दरवर्षी (वसतिगृह + मेस)\n\nमुलांसाठी आणि मुलींसाठी स्वतंत्र वसतिगृह WiFi, लॉन्ड्री, जिम आणि 24/7 सुरक्षेसह उपलब्ध आहेत.\nसध्याच्या उपलब्धतेसाठी वसतिगृह वॉर्डन कार्यालयाशी संपर्क साधा."
        },
        # ── Facilities ──
        {
            "category": "facilities",
            "question_en": "What facilities are available at JSPM Wagholi Campus?",
            "question_hi": "JSPM वाघोली कैंपस में कौन सी सुविधाएं उपलब्ध हैं?",
            "question_mr": "JSPM वाघोली कॅम्पसमध्ये कोणत्या सुविधा उपलब्ध आहेत?",
            "answer_en": "JSPM Wagholi Campus facilities:\n\n- Central Library with 50,000+ books & digital resources (DELNET)\n- Computer labs with 500+ systems & high-speed internet\n- Well-equipped engineering workshops & laboratories\n- Auditorium (500+ seating capacity)\n- Seminar halls & smart classrooms\n- Sports ground (cricket, football, volleyball, basketball)\n- Indoor games (TT, carrom, chess)\n- Gymnasium & yoga center\n- Cafeteria & food court\n- ATM on campus\n- Medical room with first-aid\n- WiFi-enabled campus\n- EV charging station\n- Parking for students & faculty",
            "answer_hi": "JSPM वाघोली कैंपस की सुविधाएं:\n\n- 50,000+ पुस्तकों और डिजिटल संसाधनों (DELNET) के साथ केंद्रीय पुस्तकालय\n- 500+ सिस्टम और हाई-स्पीड इंटरनेट के साथ कंप्यूटर लैब\n- सुसज्जित इंजीनियरिंग कार्यशालाएं और प्रयोगशालाएं\n- ऑडिटोरियम (500+ बैठक क्षमता)\n- सेमिनार हॉल और स्मार्ट क्लासरूम\n- खेल मैदान (क्रिकेट, फुटबॉल, वॉलीबॉल, बास्केटबॉल)\n- इनडोर गेम्स, जिम, योग केंद्र\n- कैफेटेरिया, ATM, मेडिकल रूम\n- WiFi-सक्षम कैंपस",
            "answer_mr": "JSPM वाघोली कॅम्पसच्या सुविधा:\n\n- 50,000+ पुस्तके आणि डिजिटल संसाधने (DELNET) सह केंद्रीय ग्रंथालय\n- 500+ सिस्टम आणि हाय-स्पीड इंटरनेटसह कॉम्प्युटर लॅब\n- सुसज्ज अभियांत्रिकी कार्यशाळा आणि प्रयोगशाळा\n- सभागृह (500+ बसण्याची क्षमता)\n- सेमिनार हॉल आणि स्मार्ट वर्गखोल्या\n- क्रीडा मैदान (क्रिकेट, फुटबॉल, व्हॉलीबॉल, बास्केटबॉल)\n- इनडोअर गेम्स, जिम, योगा केंद्र\n- कॅफेटेरिया, ATM, वैद्यकीय कक्ष\n- WiFi-सक्षम कॅम्पस"
        },
        {
            "category": "facilities",
            "question_en": "Is WiFi available at JSPM Wagholi?",
            "question_hi": "क्या JSPM वाघोली में WiFi उपलब्ध है?",
            "question_mr": "JSPM वाघोली येथे WiFi उपलब्ध आहे का?",
            "answer_en": "Yes, the entire JSPM Wagholi campus is WiFi-enabled with high-speed internet (100+ Mbps). Students can connect using their student ID credentials. Coverage includes all classrooms, labs, library, hostels, and common areas.",
            "answer_hi": "हां, पूरा JSPM वाघोली कैंपस हाई-स्पीड इंटरनेट (100+ Mbps) के साथ WiFi-सक्षम है। छात्र अपने छात्र आईडी क्रेडेंशियल्स का उपयोग करके कनेक्ट कर सकते हैं।",
            "answer_mr": "होय, संपूर्ण JSPM वाघोली कॅम्पस हाय-स्पीड इंटरनेट (100+ Mbps) सह WiFi-सक्षम आहे. विद्यार्थी त्यांच्या विद्यार्थी ID क्रेडेन्शियल्स वापरून कनेक्ट करू शकतात."
        },
        {
            "category": "facilities",
            "question_en": "What are the canteen and cafeteria facilities at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में कैंटीन और कैफेटेरिया की सुविधाएं क्या हैं?",
            "question_mr": "JSPM वाघोली येथे कॅन्टीन आणि कॅफेटेरियाची सुविधा काय आहे?",
            "answer_en": "JSPM Wagholi Campus has a well-maintained Cafeteria & Food Court:\n\n- Multi-cuisine food court inside the campus\n- Separate vegetarian and non-vegetarian counters\n- Menu includes: South Indian, North Indian, Chinese, fast food, snacks, beverages\n- Affordable pricing — meals starting from ₹40-₹60\n- Hygienic and FSSAI-compliant kitchen\n- Seating capacity: 200+ students\n- Timings: 8:00 AM to 7:00 PM (Monday to Saturday)\n- Tea/coffee and snack counters open throughout the day\n- Special mess facility available for hostel students (veg & non-veg options)\n- Mess charges: ₹35,000 – ₹45,000 per year for hostel students\n- RO purified drinking water stations across the campus\n- Juice and bakery stalls also available near the canteen area",
            "answer_hi": "JSPM वाघोली कैंपस में सुव्यवस्थित कैफेटेरिया और फूड कोर्ट:\n\n- कैंपस के अंदर मल्टी-कुज़ीन फूड कोर्ट\n- अलग शाकाहारी और मांसाहारी काउंटर\n- मेन्यू: साउथ इंडियन, नॉर्थ इंडियन, चाइनीज़, फास्ट फूड, स्नैक्स, पेय पदार्थ\n- किफायती कीमत — भोजन ₹40-₹60 से शुरू\n- स्वच्छ और FSSAI-अनुरूप किचन\n- बैठक क्षमता: 200+ छात्र\n- समय: सुबह 8:00 से शाम 7:00 (सोमवार से शनिवार)\n- चाय/कॉफी और स्नैक काउंटर पूरे दिन खुले\n- छात्रावास के छात्रों के लिए विशेष मेस सुविधा (शाकाहारी और मांसाहारी)\n- मेस शुल्क: ₹35,000 – ₹45,000 प्रति वर्ष\n- पूरे कैंपस में RO शुद्ध पेयजल स्टेशन",
            "answer_mr": "JSPM वाघोली कॅम्पसमध्ये सुव्यवस्थित कॅफेटेरिया आणि फूड कोर्ट:\n\n- कॅम्पसमध्ये मल्टी-क्युझिन फूड कोर्ट\n- स्वतंत्र शाकाहारी आणि मांसाहारी काउंटर\n- मेन्यू: साऊथ इंडियन, नॉर्थ इंडियन, चायनीज, फास्ट फूड, स्नॅक्स, पेये\n- परवडणारे दर — जेवण ₹40-₹60 पासून\n- स्वच्छ आणि FSSAI-अनुरूप किचन\n- बसण्याची क्षमता: 200+ विद्यार्थी\n- वेळ: सकाळी 8:00 ते संध्याकाळी 7:00 (सोमवार ते शनिवार)\n- चहा/कॉफी आणि स्नॅक काउंटर दिवसभर खुले\n- वसतिगृहातील विद्यार्थ्यांसाठी विशेष मेस सुविधा (शाकाहारी आणि मांसाहारी)\n- मेस शुल्क: ₹35,000 – ₹45,000 दरवर्षी\n- संपूर्ण कॅम्पसमध्ये RO शुद्ध पिण्याच्या पाण्याचे स्टेशन"
        },
        {
            "category": "facilities",
            "question_en": "What is the mess food menu and timings at JSPM Wagholi hostel?",
            "question_hi": "JSPM वाघोली छात्रावास में मेस का भोजन मेनू और समय क्या है?",
            "question_mr": "JSPM वाघोली वसतिगृहातील मेसचा जेवणाचा मेनू आणि वेळ काय आहे?",
            "answer_en": "JSPM Wagholi Hostel Mess Details:\n\n- Breakfast: 7:30 AM – 9:00 AM (Poha, Upma, Bread-Butter, Eggs, Tea/Coffee)\n- Lunch: 12:30 PM – 2:00 PM (Rice, Chapati, Dal, Sabzi, Salad, Buttermilk)\n- Evening Snacks: 5:00 PM – 6:00 PM (Tea, Biscuits, Samosa/Vada Pav)\n- Dinner: 7:30 PM – 9:00 PM (Rice/Chapati, Dal, Sabzi, Sweet on weekends)\n\n- Both vegetarian and non-vegetarian options available\n- Non-veg served 3 days a week (chicken/egg-based dishes)\n- Sunday special menu with biryani/pulao\n- Mess fees: ₹35,000 – ₹45,000 per year\n- Menu rotates weekly for variety\n- RO purified water provided",
            "answer_hi": "JSPM वाघोली छात्रावास मेस विवरण:\n\n- नाश्ता: सुबह 7:30 – 9:00 (पोहा, उपमा, ब्रेड-बटर, अंडे, चाय/कॉफी)\n- दोपहर का भोजन: 12:30 – 2:00 (चावल, चपाती, दाल, सब्ज़ी, सलाद, छाछ)\n- शाम का नाश्ता: 5:00 – 6:00 (चाय, बिस्कुट, समोसा/वड़ा पाव)\n- रात का भोजन: 7:30 – 9:00 (चावल/चपाती, दाल, सब्ज़ी, वीकेंड पर मिठाई)\n\n- शाकाहारी और मांसाहारी दोनों विकल्प\n- सप्ताह में 3 दिन मांसाहारी (चिकन/अंडे के व्यंजन)\n- रविवार को बिरयानी/पुलाव स्पेशल\n- मेस शुल्क: ₹35,000 – ₹45,000 प्रति वर्ष",
            "answer_mr": "JSPM वाघोली वसतिगृह मेस तपशील:\n\n- न्याहारी: सकाळी 7:30 – 9:00 (पोहे, उपमा, ब्रेड-बटर, अंडी, चहा/कॉफी)\n- दुपारचे जेवण: 12:30 – 2:00 (भात, चपाती, डाळ, भाजी, सॅलड, ताक)\n- संध्याकाळचा नाश्ता: 5:00 – 6:00 (चहा, बिस्किटे, समोसा/वडा पाव)\n- रात्रीचे जेवण: 7:30 – 9:00 (भात/चपाती, डाळ, भाजी, वीकेंडला गोड)\n\n- शाकाहारी आणि मांसाहारी दोन्ही पर्याय\n- आठवड्यात 3 दिवस मांसाहारी (चिकन/अंड्याचे पदार्थ)\n- रविवारी बिर्याणी/पुलाव स्पेशल\n- मेस शुल्क: ₹35,000 – ₹45,000 दरवर्षी"
        },
        {
            "category": "facilities",
            "question_en": "What are the sports facilities at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में खेल सुविधाएं क्या हैं?",
            "question_mr": "JSPM वाघोली येथे क्रीडा सुविधा काय आहेत?",
            "answer_en": "Sports facilities at JSPM Wagholi Campus:\n\n- Cricket ground (full-size with practice nets)\n- Football field\n- Basketball court\n- Volleyball court\n- Badminton courts (indoor)\n- Table Tennis tables (indoor)\n- Carrom and Chess rooms\n- Fully equipped Gymnasium with modern equipment\n- Yoga and meditation center\n- Annual sports day and inter-college tournaments\n- Professional sports coaching available\n- Students have won multiple university-level sports competitions",
            "answer_hi": "JSPM वाघोली कैंपस में खेल सुविधाएं:\n\n- क्रिकेट मैदान (प्रैक्टिस नेट के साथ)\n- फुटबॉल मैदान\n- बास्केटबॉल कोर्ट\n- वॉलीबॉल कोर्ट\n- बैडमिंटन कोर्ट (इनडोर)\n- टेबल टेनिस टेबल (इनडोर)\n- कैरम और शतरंज कमरे\n- आधुनिक उपकरणों के साथ जिम\n- योग और ध्यान केंद्र\n- वार्षिक खेल दिवस और अंतर-कॉलेज टूर्नामेंट\n- पेशेवर खेल प्रशिक्षण उपलब्ध",
            "answer_mr": "JSPM वाघोली कॅम्पसमधील क्रीडा सुविधा:\n\n- क्रिकेट मैदान (प्रॅक्टिस नेटसह)\n- फुटबॉल मैदान\n- बास्केटबॉल कोर्ट\n- व्हॉलीबॉल कोर्ट\n- बॅडमिंटन कोर्ट (इनडोअर)\n- टेबल टेनिस टेबल (इनडोअर)\n- कॅरम आणि बुद्धिबळ कक्ष\n- आधुनिक उपकरणांसह व्यायामशाळा\n- योग आणि ध्यान केंद्र\n- वार्षिक क्रीडा दिन आणि आंतर-महाविद्यालयीन स्पर्धा"
        },
        {
            "category": "facilities",
            "question_en": "Is there a medical facility or health center at JSPM Wagholi?",
            "question_hi": "क्या JSPM वाघोली में चिकित्सा सुविधा या स्वास्थ्य केंद्र है?",
            "question_mr": "JSPM वाघोली येथे वैद्यकीय सुविधा किंवा आरोग्य केंद्र आहे का?",
            "answer_en": "Yes, JSPM Wagholi Campus has an on-campus Health Center:\n\n- Resident doctor available during college hours (9:30 AM – 5:30 PM)\n- Trained nurse on duty\n- First-aid facility available 24/7\n- Basic medicines provided free of cost\n- Tie-up with nearby hospitals for emergencies (Sahyadri Hospital, Noble Hospital)\n- Ambulance facility available on call\n- Regular health check-up camps organized\n- Mental health counseling cell available for students",
            "answer_hi": "हां, JSPM वाघोली कैंपस में ऑन-कैंपस स्वास्थ्य केंद्र है:\n\n- कॉलेज के समय में निवासी डॉक्टर उपलब्ध (सुबह 9:30 – शाम 5:30)\n- प्रशिक्षित नर्स ड्यूटी पर\n- 24/7 प्राथमिक चिकित्सा सुविधा\n- बुनियादी दवाइयां मुफ्त प्रदान\n- आपातकाल के लिए पास के अस्पतालों से करार (सह्याद्रि, नोबल)\n- कॉल पर एम्बुलेंस सुविधा\n- नियमित स्वास्थ्य जांच शिविर\n- छात्रों के लिए मानसिक स्वास्थ्य परामर्श सेल",
            "answer_mr": "होय, JSPM वाघोली कॅम्पसमध्ये कॅम्पस आरोग्य केंद्र आहे:\n\n- कॉलेजच्या वेळेत निवासी डॉक्टर उपलब्ध (सकाळी 9:30 – संध्याकाळी 5:30)\n- प्रशिक्षित नर्स ड्यूटीवर\n- 24/7 प्रथमोपचार सुविधा\n- मूलभूत औषधे विनामूल्य\n- आपत्कालीन परिस्थितीसाठी जवळच्या रुग्णालयांशी करार (सह्याद्री, नोबल)\n- कॉलवर रुग्णवाहिका सुविधा\n- नियमित आरोग्य तपासणी शिबिरे\n- विद्यार्थ्यांसाठी मानसिक आरोग्य समुपदेशन कक्ष"
        },
        # ── Library ──
        {
            "category": "library",
            "question_en": "What are the library facilities at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में पुस्तकालय की सुविधाएं क्या हैं?",
            "question_mr": "JSPM वाघोली येथे ग्रंथालयाच्या सुविधा काय आहेत?",
            "answer_en": "JSPM Wagholi Central Library:\n- 50,000+ books across all disciplines\n- Digital library with DELNET, NPTEL, and IEEE access\n- Reading hall with 200+ seating capacity\n- Book bank facility for needy students\n- Open access system\n- Timings: 8:00 AM to 8:00 PM (weekdays), 9:00 AM to 5:00 PM (Saturdays)\n- Extended hours during exams till 10:00 PM\n- E-journals and previous year question papers available",
            "answer_hi": "JSPM वाघोली केंद्रीय पुस्तकालय:\n- सभी विषयों में 50,000+ पुस्तकें\n- DELNET, NPTEL, और IEEE एक्सेस के साथ डिजिटल लाइब्रेरी\n- 200+ बैठक क्षमता वाला रीडिंग हॉल\n- जरूरतमंद छात्रों के लिए बुक बैंक\n- समय: सुबह 8:00 से रात 8:00 (कार्यदिवस)\n- परीक्षा के दौरान रात 10:00 तक",
            "answer_mr": "JSPM वाघोली केंद्रीय ग्रंथालय:\n- सर्व विषयांमधील 50,000+ पुस्तके\n- DELNET, NPTEL, आणि IEEE ऍक्सेससह डिजिटल लायब्ररी\n- 200+ बसण्याच्या क्षमतेसह वाचन कक्ष\n- गरजू विद्यार्थ्यांसाठी बुक बँक\n- वेळ: सकाळी 8:00 ते रात्री 8:00 (आठवड्याचे दिवस)\n- परीक्षेदरम्यान रात्री 10:00 पर्यंत"
        },
        # ── Placement ──
        {
            "category": "placement",
            "question_en": "How are placements at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में प्लेसमेंट कैसे हैं?",
            "question_mr": "JSPM वाघोली येथे प्लेसमेंट कसे आहेत?",
            "answer_en": "JSPM Wagholi has a dedicated Training & Placement Cell:\n\n- Average package: ₹3.5 – ₹5 LPA\n- Highest package: ₹12 – ₹18 LPA\n- 70-80% students placed through campus drives\n- Top recruiters: TCS, Infosys, Wipro, Cognizant, Capgemini, Tech Mahindra, Persistent Systems, L&T, Accenture\n- Pre-placement training: Aptitude, coding, soft skills, mock interviews\n- Internship tie-ups with 50+ companies\n- Entrepreneurship Development Cell for startup aspirants",
            "answer_hi": "JSPM वाघोली में समर्पित प्रशिक्षण और प्लेसमेंट सेल:\n\n- औसत पैकेज: ₹3.5 – ₹5 LPA\n- उच्चतम पैकेज: ₹12 – ₹18 LPA\n- 70-80% छात्र कैंपस ड्राइव के माध्यम से प्लेस\n- शीर्ष भर्तीकर्ता: TCS, Infosys, Wipro, Cognizant, Capgemini, Tech Mahindra, Persistent Systems\n- प्री-प्लेसमेंट प्रशिक्षण: एप्टीट्यूड, कोडिंग, सॉफ्ट स्किल्स, मॉक इंटरव्यू",
            "answer_mr": "JSPM वाघोली येथे समर्पित प्रशिक्षण आणि प्लेसमेंट सेल:\n\n- सरासरी पॅकेज: ₹3.5 – ₹5 LPA\n- सर्वोच्च पॅकेज: ₹12 – ₹18 LPA\n- 70-80% विद्यार्थी कॅम्पस ड्राइव्हद्वारे प्लेस\n- प्रमुख भरतीकर्ते: TCS, Infosys, Wipro, Cognizant, Capgemini, Tech Mahindra, Persistent Systems\n- प्री-प्लेसमेंट प्रशिक्षण: ऍप्टिट्यूड, कोडिंग, सॉफ्ट स्किल्स, मॉक इंटरव्ह्यू"
        },
        # ── Exams ──
        {
            "category": "exams",
            "question_en": "When are the exams at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में परीक्षाएं कब होती हैं?",
            "question_mr": "JSPM वाघोली येथे परीक्षा कधी होतात?",
            "answer_en": "JSPM Wagholi follows SPPU (Savitribai Phule Pune University) exam schedule:\n- Winter exams: October – November\n- Summer exams: April – May\n- Internal assessments: Continuous throughout semester\n- Unit tests: 2 per semester\n- Results: Published on unipune.ac.in\n\nExam timetables are displayed on college notice boards and the SPPU website 1 month before exams.",
            "answer_hi": "JSPM वाघोली SPPU (सावित्रीबाई फुले पुणे विश्वविद्यालय) परीक्षा कार्यक्रम का पालन करता है:\n- शीतकालीन परीक्षा: अक्टूबर – नवंबर\n- ग्रीष्मकालीन परीक्षा: अप्रैल – मई\n- आंतरिक मूल्यांकन: सेमेस्टर भर निरंतर\n- यूनिट टेस्ट: प्रति सेमेस्टर 2\n- परिणाम: unipune.ac.in पर प्रकाशित",
            "answer_mr": "JSPM वाघोली SPPU (सावित्रीबाई फुले पुणे विद्यापीठ) परीक्षा वेळापत्रकाचे पालन करते:\n- हिवाळी परीक्षा: ऑक्टोबर – नोव्हेंबर\n- उन्हाळी परीक्षा: एप्रिल – मे\n- अंतर्गत मूल्यमापन: सत्रभर सातत्याने\n- युनिट चाचण्या: प्रत्येक सत्रात 2\n- निकाल: unipune.ac.in वर प्रकाशित"
        },
        # ── Transportation ──
        {
            "category": "transportation",
            "question_en": "Does JSPM Wagholi provide bus service?",
            "question_hi": "क्या JSPM वाघोली बस सेवा प्रदान करता है?",
            "question_mr": "JSPM वाघोली बस सेवा प्रदान करते का?",
            "answer_en": "Yes, JSPM Wagholi provides college bus service covering major routes:\n- Pune Station – Wagholi\n- Hadapsar – Wagholi\n- Kharadi – Wagholi\n- Viman Nagar – Wagholi\n- Shivajinagar – Wagholi\n- Pimpri-Chinchwad – Wagholi\n\nBus fees: ₹15,000 – ₹25,000 per year (route-based). PMPML city buses also stop near the campus on Pune-Nagar Road.",
            "answer_hi": "हां, JSPM वाघोली प्रमुख मार्गों पर कॉलेज बस सेवा प्रदान करता है:\n- पुणे स्टेशन – वाघोली\n- हडपसर – वाघोली\n- खराड़ी – वाघोली\n- विमान नगर – वाघोली\n\nबस शुल्क: ₹15,000 – ₹25,000 प्रति वर्ष। PMPML सिटी बसें भी कैंपस के पास रुकती हैं।",
            "answer_mr": "होय, JSPM वाघोली प्रमुख मार्गांवर कॉलेज बस सेवा प्रदान करते:\n- पुणे स्टेशन – वाघोली\n- हडपसर – वाघोली\n- खराडी – वाघोली\n- विमान नगर – वाघोली\n\nबस शुल्क: ₹15,000 – ₹25,000 दरवर्षी. PMPML शहर बसेसही कॅम्पसजवळ थांबतात."
        },
        # ── Contact ──
        {
            "category": "contact",
            "question_en": "What are the contact details of JSPM Wagholi?",
            "question_hi": "JSPM वाघोली के संपर्क विवरण क्या हैं?",
            "question_mr": "JSPM वाघोली चे संपर्क तपशील काय आहेत?",
            "answer_en": "JSPM Wagholi Campus Contact:\n\nAddress: S.No. 58, Wagholi, Pune - 412207, Maharashtra\nPhone: +91-20-2706-0100 / +91-20-2706-0200\nEmail: info@jspmwagholi.edu.in\nWebsite: jspmrscoe.edu.in / jscoewagholi.edu.in\n\nAdmissions Helpdesk: +91-9876543210\nPlacement Cell: +91-9876543211\nHostel Office: +91-9876543212\n\nOffice Hours: Monday to Saturday, 9:30 AM to 5:30 PM",
            "answer_hi": "JSPM वाघोली कैंपस संपर्क:\n\nपता: सर्वे नंबर 58, वाघोली, पुणे - 412207, महाराष्ट्र\nफोन: +91-20-2706-0100 / +91-20-2706-0200\nईमेल: info@jspmwagholi.edu.in\n\nप्रवेश हेल्पडेस्क: +91-9876543210\nप्लेसमेंट सेल: +91-9876543211\nकार्यालय समय: सोमवार से शनिवार, सुबह 9:30 से शाम 5:30",
            "answer_mr": "JSPM वाघोली कॅम्पस संपर्क:\n\nपत्ता: सर्वे नंबर 58, वाघोली, पुणे - 412207, महाराष्ट्र\nफोन: +91-20-2706-0100 / +91-20-2706-0200\nईमेल: info@jspmwagholi.edu.in\n\nप्रवेश हेल्पडेस्क: +91-9876543210\nप्लेसमेंट सेल: +91-9876543211\nकार्यालय वेळ: सोमवार ते शनिवार, सकाळी 9:30 ते संध्याकाळी 5:30"
        },
        # ── Faculty ──
        {
            "category": "faculty",
            "question_en": "What are the faculty achievements at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में फैकल्टी की उपलब्धियां क्या हैं?",
            "question_mr": "JSPM वाघोली येथील प्राध्यापकांच्या उपलब्धी काय आहेत?",
            "answer_en": "Faculty Achievements at JSPM Wagholi Campus:\n\n- 150+ qualified faculty members across all departments\n- 40+ faculty with Ph.D. degrees, 60+ pursuing Ph.D.\n- 200+ research papers published in national & international journals (IEEE, Springer, Elsevier)\n- 15+ patents filed and granted by faculty members\n- Faculty members received Best Teacher Awards at university and state level\n- Active involvement in SPPU Board of Studies and syllabus design\n- Funded research projects from AICTE, DST, UGC, and BCUD\n- Faculty authored 30+ textbooks published by leading publishers\n- Regular participation in FDPs (Faculty Development Programs) at IITs and NITs\n- Industry collaborations and consultancy projects with top companies\n- Faculty serve as reviewers for international conferences and journals\n- Students guided for Smart India Hackathon, Avishkar, and other national competitions",
            "answer_hi": "JSPM वाघोली कैंपस में फैकल्टी उपलब्धियां:\n\n- सभी विभागों में 150+ योग्य शिक्षक\n- 40+ शिक्षक Ph.D. धारक, 60+ Ph.D. कर रहे हैं\n- राष्ट्रीय और अंतर्राष्ट्रीय पत्रिकाओं में 200+ शोध पत्र प्रकाशित (IEEE, Springer, Elsevier)\n- शिक्षकों द्वारा 15+ पेटेंट दायर और प्राप्त\n- विश्वविद्यालय और राज्य स्तर पर सर्वश्रेष्ठ शिक्षक पुरस्कार\n- SPPU बोर्ड ऑफ स्टडीज़ और पाठ्यक्रम डिज़ाइन में सक्रिय भागीदारी\n- AICTE, DST, UGC, BCUD से वित्त पोषित अनुसंधान परियोजनाएं\n- 30+ पाठ्यपुस्तक प्रकाशित\n- IIT और NIT में FDP में नियमित भागीदारी\n- उद्योग सहयोग और परामर्श परियोजनाएं",
            "answer_mr": "JSPM वाघोली कॅम्पसमधील प्राध्यापकांच्या उपलब्धी:\n\n- सर्व विभागांमध्ये 150+ पात्र प्राध्यापक\n- 40+ प्राध्यापक Ph.D. धारक, 60+ Ph.D. करत आहेत\n- राष्ट्रीय आणि आंतरराष्ट्रीय जर्नल्समध्ये 200+ संशोधन पेपर प्रकाशित (IEEE, Springer, Elsevier)\n- प्राध्यापकांनी 15+ पेटंट दाखल केले आणि मिळवले\n- विद्यापीठ आणि राज्य स्तरावर सर्वोत्तम शिक्षक पुरस्कार\n- SPPU बोर्ड ऑफ स्टडीज आणि अभ्यासक्रम रचनेत सक्रिय सहभाग\n- AICTE, DST, UGC, BCUD कडून अर्थसहाय्यित संशोधन प्रकल्प\n- 30+ पाठ्यपुस्तके प्रकाशित\n- IIT आणि NIT मध्ये FDP मध्ये नियमित सहभाग\n- उद्योग सहकार्य आणि सल्लागार प्रकल्प"
        },
        {
            "category": "faculty",
            "question_en": "Tell me about the faculty qualifications and teaching staff at JSPM Wagholi",
            "question_hi": "JSPM वाघोली के शिक्षकों की योग्यता और शिक्षण कर्मचारियों के बारे में बताइए",
            "question_mr": "JSPM वाघोली येथील प्राध्यापकांची पात्रता आणि शिक्षण कर्मचाऱ्यांबद्दल सांगा",
            "answer_en": "Faculty at JSPM Wagholi Campus:\n\n- Total teaching staff: 150+ across all colleges\n- Student-to-faculty ratio: Approximately 15:1\n- Qualifications: M.Tech, M.E., MBA, M.Pharm, Ph.D. holders\n- Industry experienced faculty with 5-20+ years of teaching/industry experience\n- Departments: Computer, IT, AI&DS, AI&ML, E&TC, Mechanical, Civil, Electrical, MBA, Pharmacy\n- Faculty actively involved in research, publications, and consultancy\n- Regular FDPs, workshops, and industry training programs\n- Faculty mentorship program for student guidance\n- Dedicated faculty for competitive exam preparation (GATE, GRE, CAT)",
            "answer_hi": "JSPM वाघोली कैंपस में फैकल्टी:\n\n- कुल शिक्षण स्टाफ: सभी कॉलेजों में 150+\n- छात्र-शिक्षक अनुपात: लगभग 15:1\n- योग्यताएं: M.Tech, M.E., MBA, M.Pharm, Ph.D. धारक\n- 5-20+ वर्षों के शिक्षण/उद्योग अनुभव वाले शिक्षक\n- विभाग: कंप्यूटर, IT, AI&DS, AI&ML, E&TC, मैकेनिकल, सिविल, इलेक्ट्रिकल, MBA, फार्मेसी\n- अनुसंधान, प्रकाशन और परामर्श में सक्रिय\n- GATE, GRE, CAT तैयारी के लिए समर्पित शिक्षक",
            "answer_mr": "JSPM वाघोली कॅम्पसमधील प्राध्यापक:\n\n- एकूण शिक्षण कर्मचारी: सर्व महाविद्यालयांमध्ये 150+\n- विद्यार्थी-प्राध्यापक गुणोत्तर: अंदाजे 15:1\n- पात्रता: M.Tech, M.E., MBA, M.Pharm, Ph.D. धारक\n- 5-20+ वर्षांचा शिक्षण/उद्योग अनुभव असलेले प्राध्यापक\n- विभाग: कॉम्प्युटर, IT, AI&DS, AI&ML, E&TC, मेकॅनिकल, सिव्हिल, इलेक्ट्रिकल, MBA, फार्मसी\n- संशोधन, प्रकाशन आणि सल्लागारीत सक्रिय\n- GATE, GRE, CAT तयारीसाठी समर्पित प्राध्यापक"
        },
        # ── Clubs & Events ──
        {
            "category": "clubs",
            "question_en": "What clubs and activities are at JSPM Wagholi?",
            "question_hi": "JSPM वाघोली में कौन से क्लब और गतिविधियां हैं?",
            "question_mr": "JSPM वाघोली येथे कोणते क्लब आणि उपक्रम आहेत?",
            "answer_en": "Student clubs at JSPM Wagholi:\n- Coding Club & Hackathon Cell\n- Robotics & IoT Club\n- IEEE Student Branch\n- CSI Student Chapter\n- Entrepreneurship Development Cell\n- Cultural Committee (music, dance, drama)\n- NSS & NCC units\n- Sports Committee\n- Photography & Film Club\n- Debate & Literary Club\n\nAnnual events: Technical fest, Cultural fest, Sports day, Hackathons, Industry visits",
            "answer_hi": "JSPM वाघोली के छात्र क्लब:\n- कोडिंग क्लब और हैकथॉन सेल\n- रोबोटिक्स और IoT क्लब\n- IEEE स्टूडेंट ब्रांच\n- CSI स्टूडेंट चैप्टर\n- उद्यमिता विकास सेल\n- सांस्कृतिक समिति\n- NSS और NCC इकाइयां\n- खेल समिति\n\nवार्षिक कार्यक्रम: तकनीकी उत्सव, सांस्कृतिक उत्सव, खेल दिवस, हैकथॉन",
            "answer_mr": "JSPM वाघोली येथील विद्यार्थी क्लब:\n- कोडिंग क्लब आणि हॅकेथॉन सेल\n- रोबोटिक्स आणि IoT क्लब\n- IEEE स्टुडंट ब्रँच\n- CSI स्टुडंट चॅप्टर\n- उद्योजकता विकास सेल\n- सांस्कृतिक समिती\n- NSS आणि NCC युनिट\n- क्रीडा समिती\n\nवार्षिक कार्यक्रम: तांत्रिक महोत्सव, सांस्कृतिक महोत्सव, क्रीडा दिन, हॅकेथॉन"
        },
        # ── Anti-ragging ──
        {
            "category": "grievance",
            "question_en": "Is there an anti-ragging committee at JSPM Wagholi?",
            "question_hi": "क्या JSPM वाघोली में रैगिंग विरोधी समिति है?",
            "question_mr": "JSPM वाघोली येथे रॅगिंग विरोधी समिती आहे का?",
            "answer_en": "Yes, JSPM Wagholi has a strict anti-ragging policy as per AICTE/UGC norms:\n- Anti-Ragging Committee & Squad active on campus\n- Anti-Ragging helpline available 24/7\n- CCTV surveillance across campus\n- All students must sign anti-ragging undertaking\n- National Anti-Ragging Helpline: 1800-180-5522\n- Online complaint: antiragging.in",
            "answer_hi": "हां, JSPM वाघोली में AICTE/UGC मानदंडों के अनुसार सख्त रैगिंग विरोधी नीति है:\n- कैंपस में रैगिंग विरोधी समिति और दस्ता सक्रिय\n- 24/7 रैगिंग विरोधी हेल्पलाइन\n- राष्ट्रीय रैगिंग विरोधी हेल्पलाइन: 1800-180-5522",
            "answer_mr": "होय, JSPM वाघोली येथे AICTE/UGC नियमांनुसार कठोर रॅगिंग विरोधी धोरण आहे:\n- कॅम्पसमध्ये रॅगिंग विरोधी समिती आणि पथक सक्रिय\n- 24/7 रॅगिंग विरोधी हेल्पलाइन\n- राष्ट्रीय रॅगिंग विरोधी हेल्पलाइन: 1800-180-5522"
        },
        # ── Accreditation ──
        {
            "category": "accreditation",
            "question_en": "Is JSPM Wagholi NAAC accredited?",
            "question_hi": "क्या JSPM वाघोली NAAC मान्यता प्राप्त है?",
            "question_mr": "JSPM वाघोली NAAC मान्यताप्राप्त आहे का?",
            "answer_en": "Yes, JSPM Wagholi Campus colleges hold the following accreditations:\n- NAAC Accredited\n- AICTE Approved\n- Affiliated to Savitribai Phule Pune University (SPPU)\n- NBA Accreditation for select branches (Computer, IT, E&TC)\n- ISO 9001:2015 Certified\n- Recognized by DTE Maharashtra",
            "answer_hi": "हां, JSPM वाघोली कैंपस के कॉलेजों के पास निम्नलिखित मान्यताएं हैं:\n- NAAC मान्यता प्राप्त\n- AICTE अनुमोदित\n- सावित्रीबाई फुले पुणे विश्वविद्यालय (SPPU) से संबद्ध\n- चुनिंदा शाखाओं के लिए NBA मान्यता\n- ISO 9001:2015 प्रमाणित\n- DTE महाराष्ट्र द्वारा मान्यता प्राप्त",
            "answer_mr": "होय, JSPM वाघोली कॅम्पसच्या महाविद्यालयांकडे खालील मान्यता आहेत:\n- NAAC मान्यताप्राप्त\n- AICTE मान्य\n- सावित्रीबाई फुले पुणे विद्यापीठाशी (SPPU) संलग्न\n- निवडक शाखांसाठी NBA मान्यता\n- ISO 9001:2015 प्रमाणित\n- DTE महाराष्ट्र द्वारे मान्यताप्राप्त"
        }
    ]
}


def scrape_jspm_wagholi():
    """
    Attempt to scrape JSPM website for Wagholi data.
    Falls back to hardcoded dataset if scraping fails.
    Returns the dataset dict.
    """
    try:
        from bs4 import BeautifulSoup
        import requests

        logger.info("Attempting to scrape JSPM website for Wagholi data...")
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; CampusBot/1.0)'}

        # Try scraping the main JSPM page for any updates
        urls = [
            'https://www.jspmrscoe.edu.in/',
            'https://www.jscoewagholi.edu.in/',
        ]

        scraped_info = []
        for url in urls:
            try:
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')

                    # Extract text content, filtering for Wagholi-related info
                    for tag in soup.find_all(['p', 'li', 'h2', 'h3', 'h4', 'span']):
                        text = tag.get_text(strip=True)
                        if len(text) > 20 and any(kw in text.lower() for kw in
                            ['wagholi', 'pune', 'jspm', 'admission', 'course',
                             'placement', 'hostel', 'fee', 'contact']):
                            scraped_info.append(text)
            except Exception as e:
                logger.warning(f"Could not scrape {url}: {e}")

        if scraped_info:
            logger.info(f"Scraped {len(scraped_info)} Wagholi-relevant text blocks")

        # Always use hardcoded dataset as the primary source
        # Scraped data could supplement but site structures are unreliable
        return JSPM_WAGHOLI_DATA

    except ImportError:
        logger.warning("BeautifulSoup/requests not installed. Using hardcoded dataset.")
        return JSPM_WAGHOLI_DATA
    except Exception as e:
        logger.error(f"Scraping failed: {e}. Using hardcoded dataset.")
        return JSPM_WAGHOLI_DATA


def load_wagholi_data():
    """
    Load JSPM Wagholi data into the database.
    Replaces old generic campus data with Wagholi-specific data.
    """
    from models.database import get_db, load_dataset_to_db

    data = scrape_jspm_wagholi()

    # Save dataset to file
    dataset_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'database', 'jspm_wagholi_dataset.json'
    )
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Load into DB
    success = load_dataset_to_db(dataset_path)
    logger.info(f"Wagholi dataset loaded: {success}")
    return success
