- **Improving abstractive summarization on low-resource student reflections**
  - **Problem**
    - a. data requirement of neural summarization

      abstractive summarization has advanced significantly with neural seq2seq models, but complex models with thousands of parameters usually require large amounts of training data.
    - b. domain data-size contrast

      most neural summarization work is trained/tested on news domains with large datasets — CNN/DailyMail (~300k documents) and New York Times (~700k documents) — while domains like student reflections have datasets only in the tens or hundreds of documents.
    - c. hypothesis

      the authors hypothesize that training complex neural abstractive models directly in such low-resource domains will not yield good performance, and later confirm this for student reflections.
  - **Three directions explored**
    - a. domain transfer

      explored for abstractive summarization; unlike prior summarization domain-transfer studies, the training (news) and tuning (student reflection) domains here are quite dissimilar and the in-domain data is small.
    - b. template-based data synthesis

      a template-based synthesis method is proposed to create synthesized summaries, and its effect on enriching abstractive training data is compared against a synthesis baseline.
    - c. combination

      both directions are combined.
  - **Headline result**

    evaluations of neural abstractive summarization across four student reflection corpora show the utility of all three methods.
- **Related work**
  - a. abstractive summarization models
    - i. general trend

      abstractive summarization aims for coherent, readable summaries and has improved due to seq2seq models and attention mechanisms.
    - ii. pointer networks

      several works (BIBREF0, BIBREF1, BIBREF2) combine encoder-decoder-with-attention models with pointer networks to solve the out-of-vocabulary problem.
    - iii. coverage mechanism

      BIBREF0 additionally used a coverage mechanism to address word repetition.
    - iv. reinforcement learning

      BIBREF2 and BIBREF10 used reinforcement learning in an end-to-end setting.
  - b. prior domain transfer work
    - i. gap identified

      training neural abstractive models in low-resource domains via domain transfer has not been thoroughly explored outside the news domain, to the authors' knowledge.
    - ii. BIBREF4

      reports results of training on CNN/DM and evaluating on DUC without any tuning; both datasets are in the news domain and consist of well-structured, well-written documents.
    - iii. BIBREF1

      performs domain transfer experiments between two different news datasets (CNN/DM and NYT).
    - iv. differences from this paper
      - the domains here are entirely different (news vs. student reflections, which lack global structure, are repetitive, and contain sentence fragments and grammatical mistakes) — unlike the two prior news-only efforts.
      - the prior approaches either trained part of the model on NYT while keeping another part CNN/DM-only (BIBREF1), or performed no tuning at all (BIBREF4); this paper instead uses two consecutive phases — pretraining then fine-tuning.
      - BIBREF1 found domain-transfer training outperformed out-of-domain-only training but could not beat in-domain-only training, likely because their in- and out-of-domain data sizes were comparable — unlike this paper's scarce in-domain setting.
  - c. template-based prior work

    BIBREF11 develops a soft-template neural method with end-to-end template retrieval, reranking, and summary rewriting; this paper's template model differs from it in both structure and purpose.
  - d. data synthesis prior work
    - i. general state

      data synthesis for text summarization is underexplored; most prior synthesis work targets machine translation and text normalization.
    - ii. BIBREF12

      proposed data augmentation via word replacement using WordNet and vector-space similarity; this method is adopted here as a synthesis baseline.
    - iii. BIBREF14

      synthesized/augmented data via back-translation and language-model-based word replacement.
    - iv. BIBREF15

      concurrent work very close to this paper's; besides model differences, the authors judge it likely infeasible to back-generate student reflections from a human summary, especially an abstractive one.
- **Reflection summarization dataset**
  - a. collection process

    student reflections are comments given in response to instructor prompts gathering feedback on course material, collected directly after each of a set of classroom lectures over a semester; the set of reflections for one prompt in one lecture is treated as one document.
  - b. objective

    the goal is a comprehensive, meaningful abstractive summary of each student reflection document.
  - c. four course corpora

    ENGR (Introduction to Materials Science and Engineering), Stat2015 and Stat2016 (Statistics for Industrial Engineers, taught in 2015 and 2016), and CS (Data Structures in Computer Science).
  - d. two prompts

    all reflections respond to two pedagogically motivated prompts: Point of Interest (POI, "what you found most interesting") and Muddiest Point (MP, "what was confusing or needed more detail").
  - e. annotation

    at least one human (a TA or domain expert) creates a summary per reflection document; Table TABREF4 gives an example CS reference summary, and Table TABREF5 summarizes the dataset by lecture count, prompts per lecture, average reflections per prompt, and number of abstractive reference summaries per reflection set.
- **Explored approaches for limited resources**
  - a. approach 1: domain transfer

    the recent PG-net (pointer networks with coverage mechanism) model is pretrained on CNN/DM, then fine-tuned on the student reflection dataset.
  - b. approach 2: data synthesis

    a template model is proposed for synthesizing new data, motivated by the observation that reference summaries in this kind of dataset tend to share a close structure — humans identify major points students raise and present them in relative importance order (as in the CS example).
  - c. approach 3: combination

    domain transfer is combined with data synthesis.
- **Proposed template-based synthesis model**
  - a. motivation

    seq2seq synthesis models tend to generate irrelevant and repeated words, while templates yield more coherent, concise output; templates can be extracted manually or automatically with few or no trained parameters, then populated with keywords/snippets via more sophisticated models — attractive for limited-resource domains.
  - b. module 1: template extraction

    human summaries are converted into templates by removing keywords (identified via Rapid Automatic Keyword Extraction, RAKE), leaving only non-keyword text.
  - c. module 2: template clustering

    templates are embedded using a pretrained BERT model (template embedding = average-pooled word embeddings), then clustered into N clusters via k-medoid, with the goal of treating templates within a cluster as interchangeable.
  - d. module 3: summary rewriting

    an encoder-attention-decoder with a pointer network is trained to inject keywords into a template and rewrite it into a coherent paragraph; its outputs are candidate summaries.
  - e. module 4: summary selection
    - i. goal

      pick the best candidates: coherent and conveying the same meaning as the original human summary.
    - ii. hybrid scoring metric

      a weighted sum of two scores: a language-model coherence score (Eq. 1) and ROUGE-based closeness to the human summary (Eq. 2, using R-1, R-2, R-l), combined per Eq. 3 to select the top N candidates as the final synthetic set; weighting parameters α=β=1 throughout.
  - f. training the rewriting/scoring modules
    - i. training data

      a separate dataset of text snippets (sentences, paragraphs, etc.) is used to train the rewriting module and scoring LM.
    - ii. training procedure

      for each sample, keywords are extracted via RAKE and removed; the keywords plus the keyword-stripped sample are fed to the rewriting model, whose training objective is to reconstruct the original sample — effectively learning to inject extracted keywords back into a template.
  - g. model usage / generation pipeline
    - i. step 1: template extraction

      human summaries pass through template extraction, converting each summary into a template and its corresponding keywords.
    - ii. step 2: clustering

      templates are passed to the clustering module, producing clusters of similar templates.
    - iii. step 3: rewriting

      for each template and its keywords, the cluster containing that template is found, and the full set of templates in that cluster (plus the keywords) is passed to the rewriting module to produce a set of candidate summaries.
    - iv. step 4: selection

      the summary selection module scores and selects the top N candidates as synthetic summaries.
- **Experiments**
  - a. six hypotheses
    - H1: training complex abstractive models with limited in-domain or large out-of-domain data alone won't be enough to outperform extractive baselines.
    - H2: domain transfer helps abstractive models even when in-/out-of-domain data are very different and in-domain data is very small.
    - H3: enriching abstractive training data with synthetic data helps overcome in-domain data scarcity.
    - H4: the proposed template-based synthesis model outperforms a simple word replacement model.
    - H5: combining domain transfer with data synthesis outperforms using each approach alone.
    - H6: the synthesis model can be extended to perform reflection summarization directly.
  - b. extractive baselines (for H1)
    - i. baseline design rationale

      BIBREF0 used Lead-3, but reflection order doesn't matter since reflections are independent, so a random-selection-of-N-reflections baseline is used instead (averaged over 100 runs given its randomness).
    - ii. comparison baselines

      following BIBREF5, results are compared to MEAD and BIBREF5's extractive phrase-based model, both using N=5 to match the 5-phrase extraction of the comparison models; also compared against the extractive-only part of Fast-RL.
  - c. domain transfer setup (for H2, H5)
    - i. three PG-net variants

      trained on CNN/DM only, trained on reflections only, and trained on CNN/DM then tuned on reflections; Table TABREF11 shows example outputs from all three for a CS document.
    - ii. training protocol

      leave-one-course-out approach (three courses train, one tests per fold); when tuning, a combined CNN/DM + reflections dictionary avoids domain mismatch; a random 50% split of training data is used for validation to select training steps, learning rate, etc., maximizing validation ROUGE.
    - iii. implementation details

      implemented via OpenNMT with original parameters; the out-of-domain model trains 100k steps on CNN/DM; tuning lowers the learning rate from 0.15 to 0.1 for 500 additional steps; the in-domain-only model uses the same architecture, trained 20k steps with adagrad at LR 0.15.
  - d. synthesis baseline (for H3, H4)

    following BIBREF12, a WordNet-based word-replacement baseline iterates over all words in a summary; if word X has N WordNet synonyms, N new summary/reflection versions are created by substituting each synonym.
  - e. template synthesis model application (for H4, H5)
    - i. training setup

      leave-one-course-out; for each held-out course, the other three courses' data train the rewriting module and tune the scoring LM, optionally supplemented with CNN/DM summaries.
    - ii. clustering choice

      templates are clustered into 8 clusters, chosen to avoid mixing POI and MP templates (whose supporting words differ greatly) while still allowing some within-cluster diversity and avoiding excessive within-cluster dissimilarity.
    - iii. rewriting and scoring

      the rewriting model is another PG-net with identical parameters; after candidate generation, a single-layer LSTM language model — trained on 36K Wikipedia sentences and fine-tuned on student reflections — scores the candidates.
    - iv. selection count and effect

      only the top 3 scored candidates are kept per human summary (to avoid adding ill-formed summaries), which effectively triples (N=3) the size of the original reflection training data; Table TABREF11 shows a human summary, its extracted keywords, and the rewritten output using a different template.
  - f. template-based summarization (for H6)
    - i. adaptation rationale

      though designed for data synthesis, minor modification adapts the template model for direct summarization; because the modification adds few parameters, it remains suitable for small datasets.
    - ii. input change

      the input for synthesis is a summary, but for summarization the input is a set of reflections, so keyword extraction runs over the reflections instead.
    - iii. added classifier

      an extra logistic regression classifier takes the reflections as input and predicts a cluster of templates (built from other courses).
    - iv. scoring without a reference

      unlike synthesis (which scores against a reference summary), summarization has no reference at inference, so only the language-model score is used to pick the highest-scoring candidate.
- **Results**
  - a. ROUGE evaluation
    - i. metrics and table

      Table TABREF13 reports ROUGE-1, ROUGE-2, and ROUGE-L (F1), following BIBREF0's evaluation protocol, across 4 extractive baselines, original/proposed PG-net variants, and template-summarization.
    - ii. H1 support

      nearly all PG-net configurations that outperform every extractive baseline (italicized in the table) involve tuning and/or synthetic data, with one R-1 exception (row 18).
    - iii. H2 support

      comparing CNN/DM-only and reflections-only results (rows 5–6, 17–18) to their tuned counterparts (rows 9, 21) shows tuning improves R-1, R-2, and R-L for all courses; qualitatively (Table TABREF11), tuning yields more coherent and relevant summaries; the tuned model consistently beats the best baseline per course/metric except R-2 for Stat2016 (rows 9 vs. 1–4, and 21 vs. 13–16).
    - iv. H3–H5 evaluation setting

      synthesized data is tested in two settings — added to training (rows 7–8, 19–20) or added to tuning (rows 10–11, 22–23).
    - v. H4 support

      the template synthesis model beats the WordNet baseline in training (rows 7–8, 19–20, except Stat2016) and in tuning (rows 10–11, 22–23) across all courses; baseline synthetic data isn't always helpful, but template-model synthetic data helps both training and tuning.
    - vi. per-course tuning effects

      for CS and ENGR, tuning with synthetic data improves all ROUGE scores versus tuning with original data alone (rows 9 vs. 11); for Stat2015, R-1 and R-L improve while R-2 decreases; for Stat2016, R-2 and R-L improve while R-1 decreases (rows 21 vs. 23).
    - vii. H3 support

      training with reflections plus synthetic data yields improvements similar to the tuning case, compared to training on reflections alone (rows 6, 8 and 18, 20); the ROUGE increase is small but shows synthetic data benefits both training and tuning of other models.
    - viii. H5 support

      the best overall results use data synthesis for both training and tuning (rows 11 and 23).
    - ix. H6 support

      using the template model directly for summarization is surprisingly competitive; rows 12 and 24 are never the best results but come close to the best tuning-based results — attributed to the small number of trainable parameters (only the logistic regression classifier), which suits small datasets; this motivates further enhancement of the template model and exploration of less data-tailored templates.
  - b. human evaluation
    - i. rationale

      ROUGE measures lexical similarity to a reference; human judgment better captures coherence and readability, so a study tests whether tuning increases perceived coherence.
    - ii. protocol

      evaluators choose their preferred summary among three for the same document — CNN/DM-only PG-net, reflections-only PG-net, and CNN/DM-pretrained-then-reflection-tuned PG-net — presented in random order; 20 evaluators from the authors' institution each performed 20 annotations; evaluators judged only readability/coherence, without seeing the reflections or reference summary (unlike ROUGE's coverage-based comparison).
    - iii. results

      the tuned model's summaries were preferred most often: 49% (CS) and 41% (Stat2015), versus 31% (CS) and 30.9% (Stat2015) for the CNN/DM-only model, and 19.7% (CS) and 28.5% (Stat2015) for the reflections-only model — supporting that domain transfer remedies limited in-domain data and improves performance.
- **Conclusions and future work**
  - a. summary of findings

    three approaches were explored for low-resource abstractive summarization of student reflections: domain transfer, data synthesis, and their combination; pretraining PG-net on CNN/DM then tuning on reflections improved both ROUGE scores and summary readability.
  - b. synthesis contribution

    the proposed template-based synthesis model, when used to enrich training data, further increased the benefits of domain transfer/tuning on ROUGE, and outperformed a word-replacement synthesis baseline.
  - c. future plans

    trying domain adaptation, enhancing the synthesis process with other models, further exploring template-based methods, and extending the analysis to other data types such as reviews and opinions.
- **Acknowledgments**

  the research was supported in whole or in part by the Institute of Education Sciences, U.S. Department of Education, through Grant R305A180477 to the University of Pittsburgh; the opinions expressed are the authors' own and do not represent the views of the Institute or the Department of Education.
