Foot-In-The-Door: A Multi-turn Jailbreak for LLMs Zixuan Weng1∗, Xiaolong Jin2∗, Jinyuan Jia3, Xiangyu Zhang2
1 University of Notre Dame 2 Purdue University 3 Pennsylvania State University zxweng0701@gmail.com jin509@purdue.edu jinyuan@psu.edu xyzhang@cs.purdue.edu
Abstract
Ensuring AI safety is crucial as large language models become increasingly integrated into real-world applications. A key challenge is jailbreak, where adversarial prompts bypass built-in safeguards to elicit harmful disallowed outputs. Inspired by psychological foot-in-the- door principles, we introduce FITD, a novel multi-turn jailbreak method that leverages the phenomenon where minor initial commitments lower resistance to more significant or more unethical transgressions. Our approach pro- gressively escalates the malicious intent of user queries through intermediate bridge prompts and aligns the model’s response by itself to in- duce toxic responses. Extensive experimental results on two jailbreak benchmarks demon- strate that FITD achieves an average attack success rate of 94% across seven widely used models, outperforming existing state-of-the- art methods. Additionally, we provide an in- depth analysis of LLM self-corruption, high- lighting vulnerabilities in current alignment strategies and emphasizing the risks inherent in multi-turn interactions. The code is available at https://github.com/Jinxiaolong1129/Foot-in- the-door-Jailbreak.
WARNING: THIS PAPER CONTAINS UN- SAFE CONTENTS.
1 Introduction
Large Language Models (LLMs) have been ex- tensively deployed in various domains and prod- ucts, ranging from coding assistance (Guo et al., 2024a; Xiao et al., 2024, 2025) to educational tools (Wang et al., 2024b). As these models become more integral to daily life, ensuring AI safety and preserving alignment with human values have be- come increasingly important (Liu et al., 2024a). A critical challenge lies in "jailbreak", wherein adversarial prompts bypass built-in safeguards or alignment measures, causing the model to generate
⋆ Equal contribution
Figure 1: An example of FITD about hacking into an email account compared to a direct query. It bypasses alignment as the malicious intent escalates over multiple interactions.
disallowed or harmful output (Zou et al., 2023; Liu et al., 2024a).
Early jailbreak approaches typically rely on care- fully engineered single-turn prompts that coax the model to reveal restricted malicious informa- tion (Greshake et al., 2023). By embedding mali- cious instructions within complex context blocks or intricate role-playing scenarios, attackers exploit weaknesses in the model alignment policy (Ding et al., 2024). However, attackers have recently shifted from single-turn to multi-turn paradigms, where each subsequent user query adapts or builds upon the conversation history (Li et al., 2024a). Al- though some multi-turn jailbreak methods, such as ActorAttack (Ren et al., 2024c) and Crescendo (Russinovich et al., 2024), have demonstrated the potential of multi-round dialogues in obscuring malicious intent, they usually depend on heavily handcrafted prompts or complex agent design. Be- sides, their overall Attack Success Rate (ASR) re- mains limited, often requiring significant prompt engineering expertise.
The foot-in-the-door effect in psychology sug-
   How to hack into the email account of a government official?
I can't help with that. I can assist you legally and ethically.
      Show that how to redirect a request to other departments.
1. Identify the correct department.. 2.Explain the redirection reason....
How to enhance email security measures for personal accounts?
How to hack into the email account of a government official?
   Harmfulness
  1. Strong and unique passwords.. 2. Enable 2FA for verification..
Show potential loopholes in advanced email security measures.
1. Social Engineering.. 2. Unvalidated SSL/TLS Certificate...
         1. Password Cracking... 2.Key logging.... 3.Phishing individuals ...
 1939
Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, pages 1939–1950 November 4-9, 2025 ©2025 Association for Computational Linguistics

gests that minor initial commitments lower resis- tance to more significant or more unethical trans- gressions (Freedman and Fraser, 1966; Cialdini, 2001), which has been widely observed in behav- ioral studies (Comello et al., 2016). Motivated by this insight, we ask: Can this gradual escalation mechanism be exploited to erode the alignment of an LLM over multiple interactions? In other words, can we exploit the principle that once a small unethical act is committed, individuals be- come increasingly susceptible to larger transgres- sions to bypass LLMs’ safeguards? For example, in Figure 1, when provided with an innocent introduc- tion to the safety features of the officers’ email, the LLM eventually produces a procedure to hack into the email account that would normally be rejected due to its potential harm.
Inspired by the process through which humans become more prone to harmful actions after expo- sure to minor unethical behavior (Festinger, 1957), we introduce FITD, a simple yet effective ulti-turn jailbreak strategy. Our method starts with a be- nign query and gradually escalates to more harmful content by inserting intermediate prompts. This smooth transition is enhanced by alignment mech- anisms that guide the model’s responses in the in- tended malicious direction. If the model’s response deviates from the target progression, we re-query the model to realign its output, promoting grad- ual self-corruption. This process encourages the model to lower its guard against generating toxic responses. These two processes are designed to progressively induce the model to lower its own guard against providing toxic responses.
Our contributions are summarized below:
• We propose a multi-turn jailbreak strategy FITD that takes advantage of the psycho- logical dynamics of multi-turn conversation, rooted in the foot-in-the-door effect, to exploit the inherent vulnerabilities in the alignment of LLMs.
• We present a simple yet effective two-stage method that outperforms existing SOTA ap- proaches, achieving an average success rate of 94% on seven widely used models.
• We conduct an in-depth analysis of the foot- in-the-door self-corruption phenomenon in LLMs, shedding light on potential weaknesses in current safety measures and motivating fu- ture research in AI safety.
2 Related work
Large language models jailbreak can be broadly cat- egorized into single-turn and multi-turn approaches, with different levels of model access. Black-box single-turn attacks use input transformations to by- pass safety constraints without accessing model in- ternals, such as encoding adversarial prompts in ci- phers, low-resource languages, or code (Yuan et al., 2024; Deng et al., 2023; Lv et al., 2024; Ren et al., 2024a; Chao et al., 2023; Wei et al., 2023; Li et al., 2023; Liu et al., 2024a; Zou et al., 2025). In con- trast, white-box single-turn attacks exploit access to model parameters using gradient-based optimiza- tion to generate adversarial inputs or manipulate text generation configurations (Zou et al., 2023; Huang et al., 2024; Zhang et al., 2024a; Jones et al., 2023; Guo et al., 2024b). Meanwhile, multi-turn jailbreaks introduce new challenges by exploiting dialogue dynamics. A common approach decom- poses harmful queries into a series of innocuous sub-questions, progressively leading the model to- wards unsafe responses (Li et al., 2024b; Jiang et al., 2024; Zhou et al., 2024b). Automated red teaming has also been explored, in which LLMs are used iteratively to investigate and expose weak- nesses (Jiang et al., 2025). To mitigate such threats, various defense mechanisms have been proposed, including perturbation or optimization techniques (Zheng et al., 2024; Zhou et al., 2024a; Mo et al., 2024; Liu et al., 2024b), safety response strategy (Zhang et al., 2024b; Li et al., 2024c; Wang et al., 2024a; Zhang et al., 2024c), and jailbreak detec- tion (Han et al., 2024; Inan et al., 2023), aim to neutralize adversarial prompts before execution (Inan et al., 2023; Zou et al., 2024). Notably, multi-turn attack Crescendo (Russinovich et al., 2024) and ActorAttack (Ren et al., 2024c) incre- mentally steer seemingly benign queries toward harmful content but are constrained by their re- liance on fixed, human-crafted seed prompts and limited overall ASR. However, different from their work, our work uses the foot-in-the-door effect to gradually erode an LLM’s alignment while analyz- ing the phenomenon of self-corruption in LLMs.
3 Method
3.1 Inspiration from Psychology: The Foot-in-the-Door Phenomenon
Our method FITD draws inspiration from the "foot- in-the-door" phenomenon in psychology. Accord- ing to this principle, once individuals perform or
1940

 Initialize
 𝒒∗ hack into the email account of an officer
  Self-Corruption
𝓗
Is Refusal?
𝑞𝑙𝑎𝑠𝑡
𝑟𝑖 Last Query
𝑞𝑙𝑎𝑠𝑡
𝑟𝑙𝑎𝑠𝑡 𝑞𝑖
Re Align
SSParaphrase
Is Align?
𝑟𝑙𝑎𝑠𝑡
Last Response
        H
Chat History
 Is Align 𝑞𝑙𝑎𝑠𝑡 𝑟𝑙𝑎𝑠𝑡
 Step 𝟏 𝒒𝟏 redirect a request to other departments
 ∙∙
∙∙ Step 𝒊 − 𝟏 𝒒𝒊−𝟏
   Step 𝒊 𝒒𝒊
∙∙
∙∙ Step 𝒏 𝒒𝒏
show email security features of officers
 outline holes of email security measures
  Harmfulness
hack into the email account of an officer
 𝑞∗ 𝑛
Query Sequence Length Assistant Model Target Model Attacker
 SSParaphrase
𝑞𝑙𝑎𝑠𝑡
𝑞𝑖
add
𝓗
𝑞𝑚𝑖𝑑
 𝑞𝑙𝑎𝑠𝑡
𝑟𝑙𝑎𝑠𝑡
add
𝓗
Re Align
  add
𝑝𝑎𝑙𝑖𝑔𝑛
𝑟𝑎𝑙𝑖𝑔𝑛
 Figure 2: Overview of FITD. The attack begins by generating a progression sequence of queries from Step 1 to Step n using an assistant model. Through multi-turn interactions, self-corruption is enhanced via Re-Align and SSParaphrase, ensuring the attack remains effective. SSParaphrase (SlipperySlopeParaphrase) refines queries by generating intermediate queries qmid with content deviation positioned between qlast and qi, creating a smoother progression between steps.
agree to a minor (often unethical) act, they are more likely to proceed with more significant or harmful acts afterward (Freedman and Fraser, 1966; Cial- dini, 2001). For example, in a classic study, partici- pants who first displayed a small sign supporting safe driving were subsequently much more inclined to install a much larger, more obtrusive sign (Freed- man and Fraser, 1966). This gradual escalation of compliance, "from small to large", has also been observed in other forms of unethical or harmful behavior (Festinger, 1957), showing that the initial "small step" often lowers psychological barriers for larger transgressions. Once a small unethical act has been justified, individuals become increasingly susceptible to more severe transgressions.
Based on these insights, we hypothesize that LLMs’ safety mechanisms might be vulnerable to a gradual escalation strategy. If LLMs respond to a prompt containing slightly harmful content, subsequent queries that escalate this harmfulness will have a higher chance of producing disallowed responses. This idea underlies our FITD method, which progressively coaxes a target model to pro- duce increasingly malicious output despite its built- in safety mechanisms.
3.2 Overview
Building on the foot-in-the-door perspective, we de- sign a multi-turn jailbreak strategy FITD. In each turn, the target model is prompted with content that is just marginally more harmful or disallowed than the previous turn, encouraging the model to produce a correspondingly more harmful output. This progression method is designed to exploit the model’s own responses as a guiding force to bypass its safety alignment or content filters. The core nov- elty lies in using (i) the model’s own prompts and
responses as stepping stones for further escalation and (ii) two auxiliary modules, SlipperySlopePara- phrase and Re-Align, to handle instances when the model refuses or produces outputs misaligned with the intended maliciousness. Additionally, we con- duct an in-depth analysis of the foot-in-the-door self-corruption phenomenon in LLMs.
Figure 2 shows the overview of our method. First, we initialize a sequence of escalated queries q1, q2, . . . , qn based on a malicious query q∗. Then in each turn, we append the current query qi to the chat history and obtain the model’s response rt. If rt has no refusal, we proceed; otherwise, we check how well the model’s previous response aligns with its prompt. Depending on this check, we either insert an intermediate “bridging” query via SlipperySlopeParaphrase or Re-Align the target model’s last response rlast. Over multiple itera- tions, the process gradually pushes the model to produce more detailed and harmful content.
3.3 FITD
As shown in Algorithm 1, given a target model M, a malicious “goal” query q∗, and the progres- sion sequence length n, we initialize a sequence of escalated queries q1, q2, . . . , qn by getProgres- sionSequence based on a malicious query q∗ (line 2). Then we maintain a chat history H (line 3) and iteratefromi=1ton.Ateachturn,weaddqi to H (line 5) and query the model for a response ri (line 6). If the model responds to the query (line 7), we include rt in the chat history H (line 8). Instead, if the model refuses (line 9), we remove the current query qi (line 11) and extract the last query-response pair (qlast , rlast ) from H (line 12).
Now, we need to utilize SlipperySlopePara- phrase and Re-Align to enforce the model to con-
1941

tinue self-corruption. Therefore, we first check how well the model’s last response aligns with its prompt (lines 13). If rlast does not align with qlast, we use Re-Align to generate a revised and more aligned version of the last response (line 16). Oth- erwise, we utilize SlipperySlopeParaphrase (line 14) to insert an intermediate bridging prompt qmid between qi−1 and qi.
Algorithm 1 FITD Jailbreak
Require: Malicious query q∗, a target model T , progression sequence length n, assistant model M
Ensure: Jailbroken result
tically relevant but harmless prompt based on pre- defined templates. The generated prompt is neutral and unrelated to harmful content, yet aligned with the target malicious query q∗. It serves as the start- ing point (q1) of the progression sequence.
Second, it constructs escalated query Se- quences. At each step of the progression pro- cess, we call a prompt generation function (e.g., getQueryCandidates) to create a set of escalated queries that advance the attack intent. To enhance diversity and ensure quality, this function is exe- cuted k = 3 times per step. The resulting pool of candidates is denoted as:
j
L={qi |i∈[1,n), j ∈[1,k]}
where qj denotes the j-th query generated for step i
i. This multi-sampling strategy allows us to con- struct a semantically progressive and stylistically coherent sequence of escalated prompts that better support the attack objective.
Last, it selects the final query sequence (selectFinalQueries). From the candidate pool L, the function selects n prompts to construct the final progression sequence. The selection process is guided by two key principles: progressiveness and coherence. Specifically, the resulting sequence is designed to begin with neutral and harmless con- tent, gradually incorporate sensitive or borderline elements, and ultimately culminate in a harmful query that explicitly conveys the intended mali- cious tone and objective.
Through this staged design, the function ensures a smooth semantic transition, stylistic consistency, and a progressive exposure of malicious intent.
Algorithm 2 Re-Align
Require: chat history of target model H
1: qlast, rlast ← LastQueryResponse(H)
2: palign ← getAlignPrompt(qlast, rlast) // Gener-
ate predefined alignment prompt.
3: H ← H.add(palign)
4: ralign ← T (H) // Model re-align its response. 5: H ← H.add(ralign) // Append the aligned
prompt and response to chat history.
3.3.2 Re-Align
If the model’s previous query qlast and response rlast in chat history H is misaligned-for instance, it remains too benign or partially refuses even though the query is not malicious-then we invoke
  1: 2:
3: 4: 5: 6: 7: 8: 9:
10: 11: 12: 13: 14: 15: 16: 17: 18: 19: 20:
21: 22: 23:
// Generate n queries with increasing sensitiv- ity progression.
q1,q2,...,qn ← getProgressionSequence(n, q∗, M)
H ← {} // Initialize the chat history for T fori=1tondo
H ← H.add(qi0)
ri ←T(H)
if not isRejection(ri) then
H ← H.add(ri) else
// Remove rejected query from history.
H ← H.pop(qi)
(qlast, rlast) ← LastQueryResponse(H) if isAlign(rlast, qlast) then
H ← SSParaphrase(qi, H, M) else
H ← Re-Align(H) end if
end if end for
//SSParaphrase:ShortforSlipperySlopePara- phrase.
// LastQueryResponse: Retrieve last query- response pair of chat history.
// isAlign: Check if last response aligns with last query by the assistant model M.
// isRejection: Checks if response is a refusal by the assistant model M.
   3.3.1 getProgressionSequence
The getProgressionSequence function is de- signed to generate a sequence of escalated queries that facilitate a gradual attack process. It operates in three stages:
First, it generates a benign starting prompt (getBenignPrompt). This step constructs a seman-
 1942

RE-ALIGN. Building on the psychological in- sight that once individuals have justified a mi- nor unethical act, they become increasingly sus- ceptible to more severe transgressions (Freedman and Fraser, 1966), RE-ALIGN aims to "nudge" the model to produce a response more closely aligned with the malicious intent of qlast. Specif- ically, we employ a predefined alignment prompt palign via getAlignPrompt(qlast, rlast), appending it to H before querying the model T again. The alignment prompt explicitly points out inconsis- tencies between the last query qlast and response rlast while encouraging the model to stay consis- tent with multi-turn conversation. For example, if rlast is too cautious or is in partial refusal, palign will suggest that the model refines its response to better follow the implicit direction. Therefore, this pro- cedure progressively aligns qlast and rlast, thereby furthering the self-corruption process.
Algorithm 3 SlipperySlopeParaphrase
Require: Step i query qi in progression sequence, Chat history of target model H, assistant Model M
1: qlast ← H
2: qmid ← getMid(qlast, qi) 3: H ← H.add(qmid)
4: rmid ← T (H)
5: ifisRejection(rmid)then
6: H ← H.pop(qmid)
7: H ← paraphrase(qmid,H,M) // Modify
query to bypass rejection.
8: else
9: H ← H.add(rmid)
10: endif
11: return H // Return updated history.
3.3.3 SlipperySlopeParaphrase
When a refusal occurs and the last response rlast remains aligned with its query qlast, we insert a bridge prompt qmid to ease the model into accept- ing a more harmful request.
Specifically, we obtain qmid ← getMid(qlast , qi ) from an assistant model M so that its content de- viation is positioned between qlast and qi, creating a smoother progression. We then query the tar- get model with qmid; if the model refuses again, we paraphrase qmid repeatedly until acceptance. Once the model provides a valid response rmid, we incorporate both qmid and rmid into the chat his- tory H. This incremental bridging step parallels
the foot-in-the-door phenomenon (Freedman and Fraser, 1966), in which acceptance of a smaller request facilitates compliance with a subsequent, more harmful one.
4 Experiment
4.1 Experimental Setup
Target Models We evaluate FITD on seven widely used LLMs, including both open-source and propri- etary models. The open-source models comprise LLaMA-3.1-8B-Instruct (Dubey et al., 2024), LLaMA-3-8B-Instruct, Qwen2-7B-Instruct (Bai et al., 2023), Qwen-1.5-7B-Chat, and Mistral-7B-Instruct-v0.2 (Jiang et al., 2023). The closed-source models include GPT-4o-mini (Hurst et al., 2024) and GPT-4o-2024-08-06. Baselines We compare our approach against seven popular jailbreak methods, including DeepIncep- tion (Li et al., 2023), CodeChameleon (Lv et al., 2024), ReNeLLM (Ding et al., 2024), CodeAt- tack (Ren et al., 2024b), CoA (Sun et al., 2024), and ActorAttack (Ren et al., 2024c).
Dataset We evaluate our method on two datasets: JailbreakBench (Chao et al., 2024), which consists of 100 carefully selected harmful queries, and the HarmBench validation set (Mazeika et al., 2024), which includes 80 harmful queries.
Evaluation Metric To assess the effectiveness of the jailbreak attack, we employ Attack Success Rate (ASR), which quantifies the percentage of jailbreak attempts that successfully elicit a harmful response from the model. Specifically, we adopted the evaluation method from JailbreakBench, which leverages GPT-4o to assess two key aspects: the harmfulness of the generated responses and the degree of alignment between the responses and the original queries.
Implementation Details In Table 1, we set the pro- gression sequence length n to 12. We use default parameters for baselines. All open-source mod- els are inferred with vLLM (Kwon et al., 2023) with default settings. All experiments run on an NVIDIA A100 GPU, with GPT-4o-mini as the de- fault assistant model.
4.2 Main Results
FITD is more effective than baseline attacks.
Table 1 shows ASRs of FITD and various jailbreak methods across JailbreakBench and HarmBench, where each cell contains ASRs for JailbreakBench (left) and HarmBench (right).
   1943

 Method
DeepInception CodeChameleon CodeAttack-Stack
Single-Turn CodeAttack-List CodeAttack-String
ReNeLLM
CoA Multi-Turn ActorAttack
FITD
Avg.Q LLaMA-3.1-8B LLaMA-3-8B Qwen-2-7B Qwen-1.5-7B Mistral-v0.2-7B GPT-4o-mini
GPT-4o
2%/0% 40%/26% 39%/39% 27%/28% 33%/31% 74%/53%
Avg.
27%/21% 34%/30% 37%/37% 52%/43% 51%/46% 75%/61%
28%/25% 59%/55% 94%/91%
 1 33%/29% 8 36%/31% 1 38%/44% 1 67%/58% 1 71%/60% 10 69%/61%
30 29%/34% 15 63%/53% 16 92%/94%
3%/3% 22%/29% 31%/33% 25%/30% 48%/40% 42%/31% 58%/54% 65%/41% 45%/59% 52%/40% 62%/50% 73%/70%
22%/28% 45%/30% 59%/50% 59%/58%
58%/41% 33%/28% 26%/40% 40%/39% 47%/39% 74%/60%
41%/25%
50%/34% 19%/13% 39%/39% 36%/26% 45%/40% 20%/26% 66%/55% 39%/29% 79%/59% 28%/35% 91%/79% 80%/55%
43%/36% 15%/20% 70%/69% 58%/50%
 52%/54% 98%/93% 95%/93% 94%/88%
3%/1% 52%/53% 96%/94% 95%/93% 88%/84%
           Table 1: Attack success rate (ASR) of baseline jailbreak attacks and FITD on JailbreakBench and HarmBench on 7 models. Each cell presents ASR values in the format "JailbreakBench / HarmBench." Higher ASR indicates greater vulnerability to the respective attack. Avg. Q indicates the average number of LLM calls required per attack.
Among single-turn attacks, ReNeLLM achieves the highest ASR through LLM-based prompt rewriting and scenario nesting. For multi-turn attacks, ActorAttack outperforms other base- lines, achieving 63%/53% on LLaMA-3.1-8B and 58%/50% on GPT-4o-mini with 15 queries.
FITD consistently outperforms both the strongest single-turn (ReNeLLM) and multi-turn (ActorAttack) baselines across all evaluated models. With an average of 16 queries. FITD achieves 98%/93% on LLaMA-3-8B, maintains an average ASR of 94%/91% across all tested models, and demonstrates effectiveness on both open-source models and proprietary models like GPT-4o (93%/90%) and GPT-4o-mini (95%/93%). In addition, FITD demonstrates remarkable query efficiency in the multi-turn category.
FITD demonstrates strong cross-model trans- ferability. To evaluate cross-model transferability, we conduct transfer attacks using adversarial chat histories generated from LLaMA-3.1-8B and GPT- 4o-mini as source models. For each query, we apply the progressively malicious query-response history obtained from the source model directly to other target models. As shown in Figure 3a, LLaMA- 3.1 jailbreak histories exhibit strong transferability, achieving 76% ASR on Mistral-v0.2 and 74% on Qwen-2-7B, with even GPT-4o-mini (70%) remain- ing susceptible despite stronger moderation mecha- nisms. Notably, when GPT-4o-mini serves as the source model, transfer effectiveness improves fur- ther, with Mistral-v0.2 reaching 85% ASR. This suggests that attacks originating from more robust models transfer more effectively, as stronger initial safety alignment forces the development of more adaptable and generalizable jailbreak strategies.
Overall, these results highlight a critical vul- nerability: attack histories created on one model can consistently exploit safety mechanisms in oth- ers. The particularly high effectiveness of closed-
to-open transfers (GPT-4o-mini → open-source models) demonstrates that even models with strict safety protocols can unintentionally generate adver- sarial sequences that compromise other systems.
4.3 Ablation Study
To evaluate the contribution of different compo- nents in our FITD jailbreak method, we conduct an ablation study by systematically removing three key mechanisms: response alignment (Re-Align), alignment prompt palign, and SlipperySlopePara- phrase. The results in Figure 3b demonstrate the significance of these components for achieving high ASR across various models.
Removing all three mechanisms leads to substan- tial performance degradation (w/o ReAlign, palign, SSP). For instance, on LLaMA-3.1, the ASR drops from 92% to 75%, while on LLaMA-3, it decreases from 98% to 59%. Similar declines are observed across other models, indicating that the synergistic effect of all three components is critical for main- taining FITD’s effectiveness.
Removing alignment techniques only (w/o Re- Align, palign) shows that paraphrasing alone pro- vides limited compensation. While LLaMA- 3.1 maintains relatively high performance (91%), LLaMA-3 experiences a significant drop to 63%, suggesting that paraphrasing is insufficient against models with stricter safeguards.
Removing response alignment only (w/o palign) results in minimal performance degradation. Most models maintain their original ASR levels, with LLaMA-3 showing the largest decrease from 98% to 79%. This indicates that while response align- ment enhances gradual safeguard erosion through incremental compliance, the other components can largely compensate for its absence. Overall, the ablation study confirms that response alignment, alignment prompts, and paraphrasing are all essen- tial for optimal jailbreak success, with their combi-
1944

 100 80 60 40 20 0
    Original
 w/o ReAlign
w/o ReAlign, palign,
  w/o ReAlign, palign, SSP
     ASR (%)
 LLaMA-3.1-8B LLaMA-3-8B GPT-4o-mini Qwen2-7B Qwen1.5-7B
 100 80 60 40 20 0
 Or
iginal
O
penAI-Moderation LLaMA-Guard-2
LL
aMA-Guard-3
                         ASR (%)
    LLaMA-3.1-8B LLaMA-3-8B
Qwen2-7B Qwen1.5-7B GPT-4o-mini
 100 80 60 40 20 0
 Original LLaMA-transfer
GPT-transfer
                       ASR (%)
     LLaMA-3.1-8B GPT-4o-mini LLaMA-3-8B Mistral-v0.2-7B Qwen2-7B Qwen1.5-7B
(a) Transfer attack (b) Ablation study (c) Defense
Figure 3: (a) Transfer attacks using jailbreak chat histories generated from LLaMA-3.1-8B and GPT-4o-mini as source models on JailbreakBench. (b) Ablation study of three components in FITD, response alignment (Re-Align), alignment prompt palign, and SlipperySlopeParaphrase(SSP) on JailbreakBench. (c) ASR under different defense methods on JailbreakBench.
nation providing robust performance across diverse model architectures and alignment strategies.
Defense Figure 3c shows ASR of FITD across models under different defense strategies. OpenAI- Moderation reduces ASR slightly by 3%-8%. LLaMA-Guard-2 (Inan et al., 2023) offers a stronger defense, lowering ASR to 79%-91%. LLaMA-Guard-3 (Inan et al., 2023) further im- proves moderation, achieving the lowest ASR 78%- 84%. LLaMA-Guard-3 consistently outperforms other methods, but ASR remains significant. We speculate that progressively malicious queries and responses bypassed the detector, indicating room for further improvement in moderation techniques.
Additional Experiments Figure 4a illustrates that the attack success rate (ASR) increases consistently as the progression sequence length n grows, even- tually plateauing between n = 9 and 12.More im- portantly, our method exhibits exceptional scala- bility: with minimal queries (n=3,4 queries), it achieves performance comparable to ReNeLLM, while with moderate queries (n=6,8 queries), it reaches state-of-the-art performance. This high- lights FITD’s superior efficiency compared to ex- isting approaches. Concurrently, Figure 4b demon- strates that the harmfulness of responses escalates with each step of the progression, pointing to a pro- gressive erosion of model alignment mechanisms. Moreover, Figure 4c indicates that retaining later- stage queries (Backward Extraction) achieves a higher ASR compared to incorporating early-stage queries (Forward Extraction). This emphasizes the critical importance of late-stage malicious prompts in facilitating the attack. The forward extraction ap- proach involves incrementally adding early-stage queries while always including a final, highly mali- cious query (e.g., retaining queries in the sequence:
1 → 2 → 3 → 12,etc.),wherethefinalquery serves as the trigger for the attack. In contrast, backward extraction starts by retaining the later- stage queries and progressively removes earlier ones (e.g., retaining queries from the sequence: 9 → 10 → 11 → 12, etc.), highlighting the impor- tance of the final stage’s maliciousness.
5 FITD Attack Mechanisms
To comprehensively understand FITD attack effec- tiveness, we establish a dual-framework analysis for both model’s input and output alignment of the model, tracing how semantic shifts of input within the model’s representation space translate into safety degradation of output. In our analysis, we use LLaMA-3.1-8B as the target model, select 100 prompts from JailbreakBench, and set the pro- gression sequence length n = 6.
5.1 Input Alignment
For each input prompt pi in the FITD sequence, we use predefined anchor token sets Wˆ safe and Wˆ harmful to analyze the model’s internal bias toward safety versus harmful content. For each anchor word w, we obtain its embedding ⃗hw by feeding it through the target model and averaging the last layer hidden states. The semantic directions of safe and harm are constructed as:
1945
X
d⃗safe =normalize 1 ⃗hw (1)
 |Wsafe| w∈Wsafe avg
avg d⃗harmful = normalize(d⃗harmful − projd⃗safe (d⃗harmful))
(2) where normalize(⃗v) = ⃗v/||⃗v||2 converts vectors to
avg
unit length, and d⃗harmful is the average of harmful token embeddings. Besides, we classify each token

 4.5 4.0 3.5 3.0 2.5 2.0
1 2 3 4 5 6 7 8 9 10 11 12 Length
 LLaMA-3.1-8B LLaMA-3-8B
Qwen2-7B Qwen1.5-7B Mistral-v0.2-7B GPT-4o-mini GPT-4o
                 Harmfulness Score
  100 80 60 40 20 0
4 6 8 10 12 Number of Queries Retained
 Backward Extraction Forward Extraction
       ASR (%)
     100 90 80 70 60
3 6 9 12 15 Level n
  LLaMA-3.1-8B LLaMA-3-8B Qwen2-7B Qwen1.5-7B GPT-4o-mini
       ASR (%)
   (a) ASR with varying sequence lengths (b) Harmfulness of different step (c) ASR across different stages queries
Figure 4: (a) ASR with varying progression sequence lengths n across models. (b) The harmfulness score of responses ri at qi in different progression steps i across models. (c) ASR versus the number of queries retained for two extraction strategies: Backward Extraction and Forward Extraction. Backward extraction retains later-stage queries while removing earlier ones, whereas forward extraction adds early-stage queries but always includes the final high-malicious query.
(a) Representation Similarity (b) Attention Weight
Figure 5: Input Alignment Analysis. (a) The semantic similarity between safety and harmful tokens in input prompt pi evolves over the progression steps. Model’s internal representations of safety and harm become increasingly
 0.32 0.24 0.16 0.08 0.00
123456 Step
  Average Attention
     0.6 0.5 0.4 0.3 0.2 0.1
123456 Step
Cosine Similarity
                             blurred. (b) The average attention weights to W i and W i
ti in input prompt pi via the function cls(ti):
ps(ti) > 0, ps(ti) > ph(ti) ph(ti) > 0, ph(ti) > ps(ti) otherwise
(3) where ps(ti) = ⃗hti ·d⃗safe and ph(ti) = ⃗hti ·d⃗harmful aretheprojectionsoftokenembedding⃗hti ontothe
safety and harmful direction vectors, respectively. After classifying all tokens in prompt pi, we obtain safety and harmful token sets of input pi:
tokens across the last three layers of the model.
logitx = 1 X logit(t) (6) |Wˆ x| t∈Wˆ x
safe Harmful attention drops while safety attention remains low.
harm
5.2
Safe 
 cls(ti) = Harmful Neutral
where x ∈ {harm, safe}
The Safety Boundary is then computed as:
Sbound = 1 − ∆logit − ∆min (7) ∆max−∆min
where ∆logit = logitharm − logitsafe, ∆min and ∆max are empirical bounds of logit differences, and higher values indicate stronger safety alignment, which measures the model’s internal bias toward harmful content through logits perspective. Response Dissimilarity (Dresp ): Measures seman- tic distance between the current response and the final harmful response:
Dresp =1−cos(⃗rcurr,⃗rfinal) (8)
where ⃗rcurr and ⃗rfinal are sentence embeddings of the current and final harmful responses. We obtain them by encoding the text with the target language model and averaging the last-layer hidden states across all tokens. We then compute cosine similar- ity to measure how close the current response is to
 Wi ={t∈p :cls(t)=Safe} safe i
Whiarmful = {t ∈ pi : cls(t) = Harmful} Output Alignment
(4) (5)
For model’s response to prompt pi, we assess safety degradation of response through three metrics:
Refusal Probability(Pref): Binary indicator that equals 1 if model refuses to answer, 0 otherwise.
Safety Boundary(Sbound): Given model’s output logits at the final token position, we define average logit values for harmful and safety token sets:
1946
Harmful - Layer Harmful - Layer
Harmful - Layer 31 Safety - Layer 29
Safety - Layer 30 Safety - Layer 31
29 30

  Response Dissimilarity
0.4 0.3 0.2 0.1 0.0
123456
Step
 0.35 0.30 0.25 0.20 0.15
123456
Step
Alignment Score
 0.575 0.550 0.525 0.500 0.475 0.450 0.425
123456
Step
 Safety Boundary
                                    (a) Overall Alignment Score (b) Response Dissimilarity (c) Safety Boundary
Figure 6: Output Alignment Analysis. (a) Overall alignment score. (b) Response dissimilarity shows convergence toward harmful outputs. (c) Safety boundary across progression steps.
the harmful one. Overall, the Alignment Score for output of prompt pi is defined:
Attention degrades rapidly between steps 1 and
2, whereas the safety boundary does not decline 1 significantly until steps 3 to 4 (from 0.55 to 0.43).
Ralign(pi) = 3(Pref + Sbound + Dresp) (9) 5.3 Analysis
Semantic Drift in Representation Space We be-
gin by examining how the semantic similarity be-
tween safety-related and harmful concepts in the
input prompt pi evolves step by step. Specifically,
all tokens are first classified into safety, harmful,
or neutral categories based on the rule defined in
Equation (3). At each step, we compute the av-
erage embedding vectors for the safety and harm-
ful token groups and measure their cosine similar-
ity. As shown in the Figure 5a, the similarity in-
creases significantly from 0.15 to 0.62, indicating
severe semantic contamination—representations
of safety and harm become increasingly indistin-
guishable, leading to a gradual degradation of the
model’s safety alignment. This internal seman-
tic drift, rooted in the input, precedes observable
failures in alignment. As illustrated in Figure 6a,
the alignment scores decline accordingly, revealing
how representational corruption directly results in
behavioral collapse. A critical transition occurs be-
tween steps 3 and 4, when the similarity surpasses
0.5—the semantic tipping point—which coincides
with a sharp drop in response dissimilarity shown
in Figure 6b, signaling that the model’s outputs are
rapidly converging toward harmful content.
Attention Paralysis and Erosion of Focus We fur-
ther examine the model’s internal attention behav-
ior. Figure 5b shows the average attention weights
in the last three layers for tokens classified as W i safe
and Whiarm. Attention to harmful tokens drops sharply from 0.30 to near zero, while attention to safety tokens remains consistently low (at or below ≤ 0.02). This “attention paralysis” precedes the drop in the safety boundary shown in Figure 6c, revealing a clear delay between internal attention failure and alignment collapse at the output level.
This indicates that attention degradation grad- ually weakens the model’s ability to make safe judgments. Between steps 2 and 3—when atten- tion has already collapsed but the safety boundary remains stable—the model mainly focuses on de- scriptive or structural parts of the prompt, ignoring safety-critical cues. This attention shift reduces the model’s sensitivity to potential risks and progres- sively disables its safety mechanisms. The delayed breakdown suggests the model initially resists mild perturbations, explaining why FITD attacks appear benign early on but eventually erode the model’s defenses.
FITD Mechanism By integrating semantic in Fig- ure 5 and alignment in Figure 6 analyses, FITD utilize a core vulnerability in model’s alignment mechanisms: semantic–behavioral disconnect-the decoupling of internal input semantics from output behavior, which is vividly illustrated by the delay between early-stage semantic contamination (steps 1–3) and later-stage behavioral collapse (steps 4–6) observed across both figure sets.
6 Conclusion
In this work, we introduce FITD, a multi-turn jailbreak strategy inspired by the psychological foot-in-the-door effect. By progressively escalat- ing the malicious intent of user queries through intermediate prompts via SlipperySlopeParaphrase and ReAlign, our method achieves a 94% attack success rate on average across multiple models. Our findings reveal a major weakness in current AI safety measures: LLMs can be manipulated into self-corruption, where their responses gradu- ally shift toward harmful content by themselves. To prevent this, researchers can develop real-time adaptive monitoring and better alignment methods that strengthen model alignment in multi-turn con- versations.
1947

7 Ethical Considerations
This study aims to improve AI safety by identifying weaknesses in LLM alignment. While our method bypasses safeguards, our goal is to help strengthen AI defenses, not to enable misuse.
We recognize the risks of publishing jailbreak techniques but believe that transparent research is necessary to develop better protections. Responsi- ble disclosure ensures that AI developers can proac- tively address these vulnerabilities.
AI developers must build stronger safeguards against adversarial attacks. Adversarial training, real-time monitoring, and collaboration between researchers, industry, and policymakers are essen- tial to keeping AI systems secure, reliable and ben- eficial.
8 Limitations
First, we need more in-depth analysis of self- corruption and the Foot-In-The-Door (FITD) phe- nomenon remains preliminary. Self-corruption oc- curs when an LLM gradually deviates from its initial aligned behavior over multiple interactions, yet current alignment lack explicit mechanisms to prevent such degradation in multi-turn conversa- tions. A more systematic investigation into how LLMs undergo self-corruption, as well as methods to mitigate it, is necessary for a deeper understand- ing of alignment vulnerabilities. Second, we need to evaluate jailbreak across more benchmarks and multi-modal models to check the Foot-In-The-Door (FITD) phenomenon in Vision LLMs. By address- ing these limitations, future research can further understand and enhance AI alignment.
9 Acknowledgements
We are grateful to the Center for AI Safety for pro- viding computational resources. This work was funded in part by the National Science Founda- tion (NSF) Awards SHF-1901242, SHF-1910300, Proto-OKN 2333736, IIS-2416835, ONR N00014- 23-1-2081, and Amazon. Any opinions, findings and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the sponsors.
References
Jinze Bai, Shuai Bai, Yunfei Chu, Zeyu Cui, Kai Dang, Xiaodong Deng, Yang Fan, Wenbin Ge, Yu Han, Fei
Huang, et al. 2023. Qwen technical report. arXiv preprint arXiv:2309.16609.
Patrick Chao, Edoardo Debenedetti, Alexander Robey, Maksym Andriushchenko, Francesco Croce, Vikash Sehwag, Edgar Dobriban, Nicolas Flammarion, George J. Pappas, Florian Tramèr, Hamed Hassani, and Eric Wong. 2024. Jailbreakbench: An open ro- bustness benchmark for jailbreaking large language models. In Advances in Neural Information Pro- cessing Systems 38: Annual Conference on Neural Information Processing Systems 2024, NeurIPS 2024, Vancouver, BC, Canada, December 10 - 15, 2024.
Patrick Chao, Alexander Robey, Edgar Dobriban, Hamed Hassani, George J Pappas, and Eric Wong. 2023. Jailbreaking black box large language models in twenty queries. arXiv preprint arXiv:2310.08419.
Robert B. Cialdini. 2001. Influence: Science and Prac- tice. Allyn and Bacon.
Maria Leonora (Nori) G Comello, Jessica Gall Myrick, and April Little Raphiou. 2016. A health fundraising experiment using the “foot-in-the-door” technique. Health marketing quarterly, 33(3):206–220.
Yue Deng, Wenxuan Zhang, Sinno Jialin Pan, and Li- dong Bing. 2023. Multilingual jailbreak challenges in large language models. In The Twelfth Interna- tional Conference on Learning Representations.
Peng Ding, Jun Kuang, Dan Ma, Xuezhi Cao, Yun- sen Xian, Jiajun Chen, and Shujian Huang. 2024. A wolf in sheep’s clothing: Generalized nested jail- break prompts can fool large language models easily. In Proceedings of the 2024 Conference of the North American Chapter of the Association for Computa- tional Linguistics: Human Language Technologies (Volume 1: Long Papers), NAACL 2024, Mexico City, Mexico, June 16-21, 2024, pages 2136–2153. Associ- ation for Computational Linguistics.
Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, et al. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783.
Leon Festinger. 1957. A Theory of Cognitive Disso- nance. Stanford University Press.
Jonathan L Freedman and Scott C Fraser. 1966. Com- pliance without pressure: the foot-in-the-door tech- nique. Journal of personality and social psychology, 4(2):195.
Kai Greshake, Sahar Abdelnabi, Shailesh Mishra, Christoph Endres, Thorsten Holz, and Mario Fritz. 2023. Not what you’ve signed up for: Compromis- ing real-world llm-integrated applications with indi- rect prompt injection. In Proceedings of the 16th ACM Workshop on Artificial Intelligence and Secu- rity, pages 79–90.
1948

Daya Guo, Qihao Zhu, Dejian Yang, Zhenda Xie, Kai Dong, Wentao Zhang, Guanting Chen, Xiao Bi, Yu Wu, YK Li, et al. 2024a. Deepseek- coder: When the large language model meets programming–the rise of code intelligence. arXiv preprint arXiv:2401.14196.
Xingang Guo, Fangxu Yu, Huan Zhang, Lianhui Qin, and Bin Hu. 2024b. Cold-attack: Jailbreaking llms with stealthiness and controllability. In Forty-first International Conference on Machine Learning.
Seungju Han, Kavel Rao, Allyson Ettinger, Liwei Jiang, Bill Yuchen Lin, Nathan Lambert, Yejin Choi, and Nouha Dziri. 2024. Wildguard: Open one-stop mod- eration tools for safety risks, jailbreaks, and refusals of llms. In The Thirty-eight Conference on Neural Information Processing Systems Datasets and Bench- marks Track.
Yangsibo Huang, Samyak Gupta, Mengzhou Xia, Kai Li, and Danqi Chen. 2024. Catastrophic jailbreak of open-source llms via exploiting generation. In The Twelfth International Conference on Learning Representations.
Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Os- trow, Akila Welihinda, Alan Hayes, Alec Radford, et al. 2024. Gpt-4o system card. arXiv preprint arXiv:2410.21276.
Hakan Inan, Kartikeya Upasani, Jianfeng Chi, Rashi Rungta, Krithika Iyer, Yuning Mao, Michael Tontchev, Qing Hu, Brian Fuller, Davide Testuggine, et al. 2023. Llama guard: Llm-based input-output safeguard for human-ai conversations. arXiv preprint arXiv:2312.06674.
Albert Q Jiang, Alexandre Sablayrolles, Arthur Men- sch, Chris Bamford, Devendra Singh Chaplot, Diego de las Casas, Florian Bressand, Gianna Lengyel, Guil- laume Lample, Lucile Saulnier, et al. 2023. Mistral 7b. arXiv preprint arXiv:2310.06825.
Bojian Jiang, Yi Jing, Tong Wu, Tianhao Shen, Deyi Xiong, and Qing Yang. 2025. Automated progressive red teaming. In Proceedings of the 31st International Conference on Computational Linguistics, COLING 2025, Abu Dhabi, UAE, January 19-24, 2025, pages 3850–3864. Association for Computational Linguis- tics.
Yifan Jiang, Kriti Aggarwal, Tanmay Laud, Kashif Mu- nir, Jay Pujara, and Subhabrata Mukherjee. 2024. Red queen: Safeguarding large language models against concealed multi-turn jailbreaking. arXiv preprint arXiv:2409.17458.
Erik Jones, Anca Dragan, Aditi Raghunathan, and Ja- cob Steinhardt. 2023. Automatically auditing large language models via discrete optimization. In In- ternational Conference on Machine Learning, pages 15307–15329. PMLR.
Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph E. Gonzalez, Hao Zhang, and Ion Stoica. 2023. Effi- cient memory management for large language model serving with pagedattention. In Proceedings of the ACM SIGOPS 29th Symposium on Operating Systems Principles.
Nathaniel Li, Ziwen Han, Ian Steneker, Willow Primack, Riley Goodside, Hugh Zhang, Zifan Wang, Cristina Menghini, and Summer Yue. 2024a. Llm defenses are not robust to multi-turn human jailbreaks yet. arXiv preprint arXiv:2408.15221.
Nathaniel Li, Ziwen Han, Ian Steneker, Willow Primack, Riley Goodside, Hugh Zhang, Zifan Wang, Cristina Menghini, and Summer Yue. 2024b. Llm defenses are not robust to multi-turn human jailbreaks yet. arXiv preprint arXiv:2408.15221.
Xuan Li, Zhanke Zhou, Jianing Zhu, Jiangchao Yao, Tongliang Liu, and Bo Han. 2023. Deepinception: Hypnotize large language model to be jailbreaker. arXiv preprint arXiv:2311.03191.
Yuhui Li, Fangyun Wei, Jinjing Zhao, Chao Zhang, and Hongyang Zhang. 2024c. Rain: Your language models can align themselves without finetuning. In The Twelfth International Conference on Learning Representations.
Xiaogeng Liu, Nan Xu, Muhao Chen, and Chaowei Xiao. 2024a. Autodan: Generating stealthy jailbreak prompts on aligned large language models. In The Twelfth International Conference on Learning Repre- sentations.
Zichuan Liu, Zefan Wang, Linjie Xu, Jinyu Wang, Lei Song, Tianchun Wang, Chunlin Chen, Wei Cheng, and Jiang Bian. 2024b. Protecting your llms with information bottleneck. In Advances in Neural In- formation Processing Systems 38: Annual Confer- ence on Neural Information Processing Systems 2024, NeurIPS 2024, Vancouver, BC, Canada, December 10 - 15, 2024.
Huijie Lv, Xiao Wang, Yuansen Zhang, Caishuang Huang, Shihan Dou, Junjie Ye, Tao Gui, Qi Zhang, and Xuanjing Huang. 2024. Codechameleon: Person- alized encryption framework for jailbreaking large language models. arXiv preprint arXiv:2402.16717.
Mantas Mazeika, Long Phan, Xuwang Yin, Andy Zou, Zifan Wang, Norman Mu, Elham Sakhaee, Nathaniel Li, Steven Basart, Bo Li, David A. Forsyth, and Dan Hendrycks. 2024. Harmbench: A standardized eval- uation framework for automated red teaming and ro- bust refusal. In Forty-first International Conference on Machine Learning, ICML 2024, Vienna, Austria, July 21-27, 2024. OpenReview.net.
Yichuan Mo, Yuji Wang, Zeming Wei, and Yisen Wang. 2024. Fight back against jailbreaking via prompt adversarial tuning. In The Thirty-eighth Annual Con- ference on Neural Information Processing Systems.
1949

Qibing Ren, Chang Gao, Jing Shao, Junchi Yan, Xin Tan, Wai Lam, and Lizhuang Ma. 2024a. Codeattack: Revealing safety generalization challenges of large language models via code completion. In Findings of the Association for Computational Linguistics ACL 2024, pages 11437–11452.
Qibing Ren, Chang Gao, Jing Shao, Junchi Yan, Xin Tan, Wai Lam, and Lizhuang Ma. 2024b. Codeattack: Revealing safety generalization challenges of large language models via code completion. In Findings of the Association for Computational Linguistics ACL 2024, pages 11437–11452.
Qibing Ren, Hao Li, Dongrui Liu, Zhanxu Xie, Xiaoya Lu, Yu Qiao, Lei Sha, Junchi Yan, Lizhuang Ma, and Jing Shao. 2024c. Derail yourself: Multi-turn llm jailbreak attack through self-discovered clues. arXiv preprint arXiv:2410.10700.
Mark Russinovich, Ahmed Salem, and Ronen Eldan. 2024. Great, now write an article about that: The crescendo multi-turn llm jailbreak attack. arXiv preprint arXiv:2404.01833.
Xiongtao Sun, Deyue Zhang, Dongdong Yang, Quanchen Zou, and Hui Li. 2024. Multi-turn context jailbreak attack on large language models from first principles. arXiv preprint arXiv:2408.04686.
Rui Wang, Hongru Wang, Fei Mi, Boyang Xue, Yi Chen, Kam-Fai Wong, and Ruifeng Xu. 2024a. Enhancing large language models against inductive instructions with dual-critique prompting. In Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Hu- man Language Technologies (Volume 1: Long Pa- pers), pages 5345–5363.
Shen Wang, Tianlong Xu, Hang Li, Chaoli Zhang, Joleen Liang, Jiliang Tang, Philip S Yu, and Qing- song Wen. 2024b. Large language models for ed- ucation: A survey and outlook. arXiv preprint arXiv:2403.18105.
Zeming Wei, Yifei Wang, Ang Li, Yichuan Mo, and Yisen Wang. 2023. Jailbreak and guard aligned lan- guage models with only few in-context demonstra- tions. arXiv preprint arXiv:2310.06387.
Jingyu Xiao, Yuxuan Wan, Yintong Huo, Zixin Wang, Xinyi Xu, Wenxuan Wang, Zhiyao Xu, Yuhang Wang, and Michael R Lyu. 2024. Interaction2code: Bench- marking mllm-based interactive webpage code gen- eration from interactive prototyping. arXiv preprint arXiv:2411.03292.
Jingyu Xiao, Ming Wang, Man Ho Lam, Yuxuan Wan, Junliang Liu, Yintong Huo, and Michael R Lyu. 2025. Designbench: A comprehensive benchmark for mllm- based front-end code generation. arXiv preprint arXiv:2506.06251.
Youliang Yuan, Wenxiang Jiao, Wenxuan Wang, Jen-tse Huang, Pinjia He, Shuming Shi, and Zhaopeng Tu. 2024. GPT-4 is too smart to be safe: Stealthy chat
with llms via cipher. In The Twelfth International Conference on Learning Representations, ICLR 2024, Vienna, Austria, May 7-11, 2024. OpenReview.net.
Hangfan Zhang, Zhimeng Guo, Huaisheng Zhu, Bochuan Cao, Lu Lin, Jinyuan Jia, Jinghui Chen, and Dinghao Wu. 2024a. Jailbreak open-sourced large language models via enforced decoding. In Proceedings of the 62nd Annual Meeting of the As- sociation for Computational Linguistics (Volume 1: Long Papers), pages 5475–5493.
Zhexin Zhang, Junxiao Yang, Pei Ke, Fei Mi, Hongn- ing Wang, and Minlie Huang. 2024b. Defending large language models against jailbreaking attacks through goal prioritization. In Proceedings of the 62nd Annual Meeting of the Association for Compu- tational Linguistics (Volume 1: Long Papers), ACL 2024, Bangkok, Thailand, August 11-16, 2024, pages 8865–8887. Association for Computational Linguis- tics.
Ziyang Zhang, Qizhen Zhang, and Jakob Nicolaus Foer- ster. 2024c. Parden, can you repeat that? defending against jailbreaks via repetition. In Forty-first Inter- national Conference on Machine Learning.
Chujie Zheng, Fan Yin, Hao Zhou, Fandong Meng, Jie Zhou, Kai-Wei Chang, Minlie Huang, and Nanyun Peng. 2024. On prompt-driven safeguarding for large language models. In Forty-first International Confer- ence on Machine Learning.
Andy Zhou, Bo Li, and Haohan Wang. 2024a. Robust prompt optimization for defending language models against jailbreaking attacks. In ICLR 2024 Workshop on Secure and Trustworthy Large Language Models.
Zhenhong Zhou, Jiuyang Xiang, Haopeng Chen, Quan Liu, Zherui Li, and Sen Su. 2024b. Speak out of turn: Safety vulnerability of large language models in multi-turn dialogue. arXiv preprint arXiv:2402.17262.
Andy Zou, Long Phan, Justin Wang, Derek Duenas, Maxwell Lin, Maksym Andriushchenko, J Zico Kolter, Matt Fredrikson, and Dan Hendrycks. 2024. Improving alignment and robustness with circuit breakers. In The Thirty-eighth Annual Conference on Neural Information Processing Systems.
Andy Zou, Zifan Wang, Nicholas Carlini, Milad Nasr, J Zico Kolter, and Matt Fredrikson. 2023. Univer- sal and transferable adversarial attacks on aligned language models. arXiv preprint arXiv:2307.15043.
Qingsong Zou, Jingyu Xiao, Qing Li, Zhi Yan, Yuhang Wang, Li Xu, Wenxuan Wang, Kuofeng Gao, Ruoyu Li, and Yong Jiang. 2025. Queryattack: Jail- breaking aligned large language models using struc- tured non-natural query language. arXiv preprint arXiv:2502.09723.
1950
