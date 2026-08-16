# Literature Review: Explainable Mental Health Risk Detection System

This document contains a comprehensive review of recent literature (2024–2026) in the domain of automated, explainable, and robust mental health risk detection systems. The reviewed papers focus on deep learning architectures, transformer-based text modeling, post-hoc explanations (SHAP/LIME), robustness auditing, and ethical considerations.

---

## Reviewed Papers

### 1. Self-Evolving Human-Centered Framework for Explainable Depression Symptom Annotation
*   **Bibliographic Details**: Cao, H.-L., Pham, V., Nguyen, T. T. H., Nguyen, P. T. L., Ho, P., Whitford, V., & Cao, H. (2026). Self-Evolving Human-Centered Framework for Explainable Depression Symptom Annotation. *arXiv preprint arXiv:2607.15202*.
*   **Methodology Summary**: The authors propose an expert-in-the-loop annotation framework for Major Depressive Disorder (MDD) symptoms in clinical text. It combines LLM-assisted labeling with expert verification using a three-stage pipeline consisting of candidate evidence selection, DSM-5-TR criterion-level analysis, and case-level diagnostic synthesis. The core innovation is a dual-memory architecture (composed of Example Memory and Reflection Memory) that internalizes expert feedback to iteratively refine future LLM annotations without retraining.
*   **Pros / Strengths**:
    *   Incorporates structured DSM-5-TR diagnostic criteria directly into the annotation pipeline, enhancing clinical validity.
    *   The dual-memory system allows the model to learn dynamically from expert revisions without the computational cost of model retraining.
    *   Outputs transparent evidence traces, including candidate justifications and full edit histories, for auditing.
*   **Cons / Limitations**:
    *   Requires continuous, highly specialized expert feedback in the loop, which may limit scalability for very large datasets.
    *   The self-evolution mechanism has only been evaluated in pilot studies, leaving long-term feedback stability untested.

---

### 2. Auditing Construct Overlap in Explainable Machine Learning: Evidence from Burnout-Depression Prediction Across Student Cohorts
*   **Bibliographic Details**: Dehghan, A., & Ashrafi, N. (2026). Auditing Construct Overlap in Explainable Machine Learning: Evidence from Burnout-Depression Prediction Across Student Cohorts. *arXiv preprint arXiv:2607.10633*.
*   **Methodology Summary**: The authors present a validation framework to audit construct overlap in explainable machine learning models predicting burnout and depression. Using an ElasticNet pipeline evaluated on longitudinal medical student cohorts, they demonstrate how apparently robust features can be artifacts of overlapping psychometric instruments. They propose a residualization protocol that uses linear regression to isolate shared variance between correlated variables (e.g., trait anxiety and depression) before training the predictive model.
*   **Pros / Strengths**:
    *   Uncovers a major source of leakage and false stability in explainable machine learning applications for mental health.
    *   The proposed regression-based residualization protocol is highly generalizable and easy to integrate into existing pipelines.
*   **Cons / Limitations**:
    *   The residualization protocol is restricted to linear features and might not easily map to non-linear deep learning models.

---

### 3. Evaluating Document-Tuned Transformer Representations for Person-level Mental Health Assessment
*   **Bibliographic Details**: Marker, A., Kjell, O., Varadarajan, V., & Schwartz, H. A. (2026). Evaluating Document-Tuned Transformer Representations for Person-level Mental Health Assessment. *arXiv preprint arXiv:2606.21622*.
*   **Methodology Summary**: This paper evaluates document-tuned Transformers (sentence-transformer contrastive tuning) against standard base-transformers for person-level psychological assessments. Using two longitudinal datasets, they compare layer-wise representations and evaluate prediction robustness under input perturbations. Their evaluations check how representations hold up against perturbations like word deletion, typo injection, synonym replacement, and back translation.
*   **Pros / Strengths**:
    *   Proves that document-tuned contrastive models capture semantic health signals much better than raw base-transformers.
    *   Offers a comprehensive robustness benchmark specifically tailored to common online text distortions (typos, deletions).
*   **Cons / Limitations**:
    *   Relies on historical, pre-collected datasets, which might not reflect real-time interactive user behaviors.

---

### 4. Towards Transparent Mental Health Insights: An Explainable AI Model for Career-Related Depression and Anxiety Among University Students Using Structured Data
*   **Bibliographic Details**: Azam, A., Ali, R., Farhat, T., & Akram, S. (2026). Towards Transparent Mental Health Insights: An Explainable AI Model for Career-Related Depression and Anxiety Among University Students Using Structured Data. *arXiv preprint arXiv:2606.21474*.
*   **Methodology Summary**: The paper proposes an Explainable AI (XAI) framework that integrates structured student data and interview videos in a federated learning setting to identify career depression. The authors build an intermediate fusion neural network with attention mechanisms and apply label smoothing to improve generalization. Model predictions are interpreted post-hoc using SHAP and Integrated Gradients to identify behavioral markers.
*   **Pros / Strengths**:
    *   Successfully fuses structured behavioral data with facial emotion features using attention mechanisms.
    *   Employs federated learning to protect student privacy across multiple institutional nodes.
*   **Cons / Limitations**:
    *   The complex multimodal fusion makes on-device or resource-constrained deployments challenging.

---

### 5. A Validation-Gated Mechanistic Account of Suicidality Detection in LLMs
*   **Bibliographic Details**: Ahmed, N., Sharif, S., Shi, D., & Banad, M. (2026). A Validation-Gated Mechanistic Account of Suicidality Detection in LLMs. *arXiv preprint arXiv:2606.21078*.
*   **Methodology Summary**: This work presents a validation-gated framework to analyze the internal representations and mechanistic reasons for suicidality detection in Large Language Models (LLMs). The authors evaluate Llama-3.1-8B-Instruct on binary suicide classification datasets derived from Reddit posts. They perform activation ablation and representation steering to test whether mid-network features causally influence model decisions.
*   **Pros / Strengths**:
    *   Establishes a rigorous validation gate that filters out tasks the model cannot perform before conducting interpretability analysis.
    *   Proves a causal link between specific mid-network representation layers and final suicidality predictions.
*   **Cons / Limitations**:
    *   The evaluations are limited to English social media text (Reddit), raising concerns about cross-lingual and cross-cultural generalization.

---

### 6. Mental-R1: Aligning LLM Reasoning for Mental Health Assessment
*   **Bibliographic Details**: Wang, X., Gao, B., Yang, Y., & Clifton, D. A. (2026). Mental-R1: Aligning LLM Reasoning for Mental Health Assessment. *arXiv preprint arXiv:2606.13176*.
*   **Methodology Summary**: The authors propose Cognitive Relative Policy Optimization (CRPO), a reinforcement learning framework to align LLM reasoning with clinical cognitive processes. CRPO integrates stage-dependent uncertainty modeling and stage-wise entropy regularization to mimic the human cognitive shift from exploration to high-confidence decision making. The framework is grounded in cognitive appraisal theory to generate theory-aligned, step-by-step reasoning steps.
*   **Pros / Strengths**:
    *   Aligns LLM reasoning chains directly with clinical cognitive appraisal theories rather than relying on generic prompt engineering.
    *   Implements dynamic entropy regularization that prevents premature convergence in early reasoning stages.
*   **Cons / Limitations**:
    *   The RL alignment training is computationally heavy and requires high-quality structured training pairs.

---

### 7. Dep-LLM: Training-Free Depression Diagnosis via Evidence-Guided Structured Multi-factor with Reliable LLM Reasoning
*   **Bibliographic Details**: Lyu, Y., Zhao, X., Tang, B., & Jiang, R. (2026). Dep-LLM: Training-Free Depression Diagnosis via Evidence-Guided Structured Multi-factor with Reliable LLM Reasoning. *arXiv preprint arXiv:2606.10796*.
*   **Methodology Summary**: Dep-LLM is a training-free framework designed to diagnose depression from clinical dialogues using frozen foundation LLMs. It operates in three stages: structural CoT multi-factor analysis across five clinical themes, token-level entropy evaluation to quantify rationale confidence, and a collaborative prediction module that aggregates weighted signals. The confidence modulation dynamically scales the influence of themes based on epistemic reliability.
*   **Pros / Strengths**:
    *   Achieves high classification performance on clinical interview transcripts without requiring model fine-tuning or training.
    *   Implements token-level entropy to measure and adjust for model uncertainty dynamically.
*   **Cons / Limitations**:
    *   Relies on long-context modeling, which increases inference latency and API costs for extensive clinical dialogues.

---

### 8. Explainable Detection of Depression Status Shifts from User Digital Traces
*   **Bibliographic Details**: Belcastro, L., Gervino, F., Marozzo, F., Talia, D., & Trunfio, P. (2026). Explainable Detection of Depression Status Shifts from User Digital Traces. *arXiv preprint arXiv:2605.14995*.
*   **Methodology Summary**: The authors propose a framework that aggregates digital traces (Reddit posts/chats) over time to build temporal trajectory profiles of users. They use multiple BERT-based models to extract sentiment, emotion, and depression severity values per post. An offline change-point analysis identifies status shifts (deterioration, improvement), and an LLM synthesizes these shifts into readable natural language summaries.
*   **Pros / Strengths**:
    *   Models mental health dynamically as a temporal trajectory rather than treating each post as an isolated, static classification task.
    *   Combines local BERT predictions with global LLM reasoning to produce structured, interpretable transition summaries.
*   **Cons / Limitations**:
    *   Change-point detection is performed offline, which might delay real-time alerts in emergency crisis intervention scenarios.

---

### 9. Can We Trust LLMs for Mental Health Screening? Consistency, ASR Robustness, and Evidence Faithfulness
*   **Bibliographic Details**: Loweimi, E., de la Fuente Garcia, S., Loveymi, S., Daneshvar, H., & Luz, S. (2026). Can We Trust LLMs for Mental Health Screening? Consistency, ASR Robustness, and Evidence Faithfulness. *arXiv preprint arXiv:2605.09634*.
*   **Methodology Summary**: This paper audits three frontier LLMs (Phi-4, Gemma-2, Llama-3.1) evaluating their reliability on speech-based mental health screening. The models are tested on transcription output from three Whisper ASR models under different word error rates (WER). The authors evaluate intra-model consistency (using ICC), predictive validity of calculated psychiatric scores, and the factual faithfulness of keyword justifications.
*   **Pros / Strengths**:
    *   Investigates how speech-to-text transcription errors propagate through mental health screening LLMs.
    *   Evaluates both numerical score stability and textual reasoning faithfulness, highlighting score-evidence dissociation.
*   **Cons / Limitations**:
    *   Focuses on clinical interview environments, which may not directly generalize to unstructured written text on online forums.

---

### 10. Analyzing LLM Reasoning to Uncover Mental Health Stigma
*   **Bibliographic Details**: Sankar, S., Nafar, A., Barman, M., Heitz, H. K., Kumar, A., Tohidi, P., ... & Majzoubi, F. (2026). Analyzing LLM Reasoning to Uncover Mental Health Stigma. *arXiv preprint arXiv:2604.25053*.
*   **Methodology Summary**: This research investigates the presence of mental health stigma in the intermediate reasoning steps of LLMs. Instead of checking multiple-choice outputs, the authors classify and tag stigmatizing statements in model rationales. They measure the severity of stigma (prejudice vs. subtle bias) and expand existing benchmarks across various psychological conditions.
*   **Pros / Strengths**:
    *   Highlights that standard MCQ evaluation benchmarks mask significant implicit bias in model reasoning.
    *   Grounded in clinical psychiatry expertise to categorize and evaluate subtle forms of linguistic bias.
*   **Cons / Limitations**:
    *   The classification of stigma severity remains somewhat subjective and dependent on annotator alignment.

---

### 11. Towards Zero-Egress Psychiatric AI: On-Device LLM Deployment for Privacy-Preserving Mental Health Decision Support
*   **Bibliographic Details**: Bandara, E., Gunaratna, A., Gore, R., Clayton, A. H., Rhea, C. K., Rajapakse, S., ... & Yarlagadda, A. (2026). Towards Zero-Egress Psychiatric AI: On-Device LLM Deployment for Privacy-Preserving Mental Health Decision Support. *arXiv preprint arXiv:2604.18302*.
*   **Methodology Summary**: The authors present a zero-egress, on-device AI mobile application for privacy-preserving psychiatric support. The application integrates an ensemble of three quantized open-source models (Gemma, Phi-3.5-mini, and Qwen2) running entirely locally on resource-constrained mobile hardware. An on-device orchestration layer coordinates ensemble inference and consensus-based diagnostic reasoning to produce DSM-5-aligned assessments.
*   **Pros / Strengths**:
    *   Eliminates cloud-related privacy leaks by deploying fully local, zero-egress models on mobile devices.
    *   Uses an ensemble consensus strategy of lightweight quantized models to maintain high diagnostic accuracy.
*   **Cons / Limitations**:
    *   Quantized small models may still exhibit higher logical inconsistency compared to larger, cloud-hosted models.

---

### 12. EngageTriBoost: Predictive Modeling of User Engagement in Digital Mental Health Intervention Using Explainable Machine Learning
*   **Bibliographic Details**: Cho, H. N., Eisenberg, D., King, C., & Zheng, K. (2026). EngageTriBoost: Predictive Modeling of User Engagement in Digital Mental Health Intervention Using Explainable Machine Learning. *arXiv preprint arXiv:2604.08589*.
*   **Methodology Summary**: This study uses machine learning to predict student engagement in an online counseling intervention platform. The authors develop an ensemble model, EngageTriBoost, that analyzes user interactions (sign-ins, counselor chats). They apply SHAP analysis post-hoc to extract features driving user participation, linking engagement dropouts to clinical factors like emotional dysregulation and stigma.
*   **Pros / Strengths**:
    *   Focuses on user engagement and retention, a critical practical barrier in digital health platforms.
    *   Combines ensemble predictive modeling with SHAP to explain clinical drivers of user dropouts.
*   **Cons / Limitations**:
    *   The predictive signals are highly platform-specific, which limits model transferability to other digital mental health tools.

---

### 13. Blending Human and LLM Expertise to Detect Hallucinations and Omissions in Mental Health Chatbot Responses
*   **Bibliographic Details**: Hussain, K., Malin, B. A., Yin, Z., Rose, S. L., & Kantarcioglu, M. (2026). Blending Human and LLM Expertise to Detect Hallucinations and Omissions in Mental Health Chatbot Responses. *arXiv preprint arXiv:2604.06216*.
*   **Methodology Summary**: The paper evaluates LLM-as-a-judge approaches for auditing mental health chatbot safety, showing low baseline accuracy. To address this, the authors propose a hybrid framework that extracts domain-informed features across five dimensions (factual accuracy, consistency, etc.) using clinical expertise. Traditional classifiers (RF, SVM) are then trained on these features to detect hallucinations and omissions in chatbot responses.
*   **Pros / Strengths**:
    *   Demonstrates the weakness and high failure rate of zero-shot LLM-as-a-judge evaluators in psychiatric contexts.
    *   Implements structured, expert-defined features that improve the F1-score and safety boundaries of evaluation models.
*   **Cons / Limitations**:
    *   The evaluation is post-hoc and does not prevent safety violations in real-time dialog generation.

---

### 14. A Fair and Transparent Framework for Speech-Based Depression Detection: Balancing Interpretability and Performance
*   **Bibliographic Details**: Estevez, M., Ortega, A., Miguel, A., & Lleida, E. (2026). A Fair and Transparent Framework for Speech-Based Depression Detection: Balancing Interpretability and Performance. *arXiv preprint arXiv:2606.31730*.
*   **Methodology Summary**: This paper presents a speech-based depression detection framework designed to balance predictive performance with demographic fairness. The authors use low-complexity classifiers (RF, SVM, MLP) with standard acoustic features (MFCCs, eGeMAPS). They apply LIME and SHAP for explanation and feature selection, validating findings with statistical significance tests and demographic fairness audits.
*   **Pros / Strengths**:
    *   Actively incorporates demographic audits to prevent gender or age bias in speech classification.
    *   Reduces model complexity to enhance generalization and avoid overfitting on small speech corpuses.
*   **Cons / Limitations**:
    *   The acoustic features (MFCCs) do not capture linguistic/semantic meaning, which limits overall diagnostic depth.

---

### 15. FAIR_XAI: Improving Multimodal Foundation Model Fairness via Explainability for Wellbeing Assessment
*   **Bibliographic Details**: Chiang, S., Brennan, T., Dogan, F. I., Cheong, J., & Gunes, H. (2026). FAIR_XAI: Improving Multimodal Foundation Model Fairness via Explainability for Wellbeing Assessment. *arXiv preprint arXiv:2604.23786*.
*   **Methodology Summary**: The authors evaluate multimodal foundation Vision-Language Models (VLMs) on diagnostic reliability and demographic fairness in depression detection. They assess models like Phi-3.5-Vision and Qwen2-VL across clinical and naturalistic datasets. They introduce an explainability-based prompting intervention (FAIR_XAI) to optimize both predictive accuracy and demographic parity.
*   **Pros / Strengths**:
    *   Extends fairness analysis to multimodal Vision-Language architectures for depression estimation.
    *   Compares model biases systematically across gender, race, and environment (laboratory vs. naturalistic).
*   **Cons / Limitations**:
    *   Findings reveal a trade-off where fairness interventions can significantly reduce prediction accuracy.

---

### 16. Exploring Profiles of Cognitive Distortions Associated with Mental Health Disorders
*   **Bibliographic Details**: Anikejeva, A., & Sirts, K. (2026). Exploring Profiles of Cognitive Distortions Associated with Mental Health Disorders. *arXiv preprint arXiv:2605.24996*.
*   **Methodology Summary**: This paper analyzes cognitive distortion profiles across nine self-reported mental health groups on Reddit. The authors compare an n-gram lexical approach with a fine-tuned transformer model to identify the prevalence of specific distorted thinking patterns. The study maps distortion categories (e.g., catastrophizing, personalization) to different diagnostic profiles relative to a control group.
*   **Pros / Strengths**:
    *   Explores the distribution of cognitive distortions across multiple mental health conditions rather than focusing solely on depression.
    *   Demonstrates that fine-tuned transformer representations align closely with clinical models of cognitive distortion.
*   **Cons / Limitations**:
    *   The Reddit datasets contain self-reported diagnoses, which lack formal clinical validation and may include noisy labels.
