- **Fast-prototyped dialogue comprehension for nurse-patient calls**
  - **Problem statement**
    - a. spoken conversation's role

      spoken conversation remains the most natural and effortless means of human communication, so a lot of valuable information is exchanged in this unstructured form.
    - b. telehealth use case

      in telehealth settings, nurses may call discharged patients at home to continue monitoring their health status; technology that can efficiently and effectively extract key information from such conversations is clinically useful for streamlining workflows and digitally documenting patient medical information, increasing staff productivity.
    - c. what the paper builds

      the paper designs and prototypes a question-answering-style dialogue comprehension system that comprehends spoken nurse-patient conversations to extract clinical information.
  - **Motivation of approach**
    - a. progress in written-passage comprehension

      machine comprehension of written passages has advanced greatly, driven by large supervised datasets (e.g. SQuAD), widespread neural modeling, and advances in word-embedding representations; the first factor (large-scale data) is what empowers the latter two.
    - b. dialogue-data scarcity

      well-annotated large-scale data suitable for modeling human-human spoken dialogue remains very limited, so directly porting reading-comprehension advances to dialogue comprehension isn't straightforward.
    - c. healthcare-specific scarcity

      conversation data is scarcer still in healthcare due to privacy concerns; crowd-sourcing, though efficient for large-scale annotation elsewhere, is less suitable here since domain knowledge is needed to ensure data quality.
    - d. response: simulated dataset

      to demonstrate feasibility, a framework is developed to construct a simulated human-human dialogue dataset to bootstrap the prototype; similar efforts exist for human-machine dialogue in restaurant/movie reservation domains, but, to the authors' knowledge, none for human-human healthcare conversations.
  - **Result**

    a bi-directional attention pointer network trained on the simulated dataset achieves over 80% F1 score on a held-out test set of real-world nurse-patient conversations, demonstrating feasible extraction, retrieval, and comprehension of symptom-checking information from multi-turn human-human spoken conversation.
- **Human-human spoken conversation challenges**
  - a. zero anaphora
    - i. prevalence

      co-reference resolution across multiple speakers' spoken utterances is needed more often than in text; e.g. "headaches," "the pain," "it," and "head bulging" all refer to a single headache symptom but are uttered by different speakers across multiple utterances/turns.
    - ii. omission

      anaphors are also more likely to be omitted in speech, which doesn't hinder human listener comprehension but is challenging for computational models.
  - b. thinking aloud
    - i. cause

      speaking is more effortless than typing, so speakers more readily reveal their running thoughts; unlike text, spoken utterances cannot be retracted once said, whereas written responses are typically checked/revised before sending.
    - ii. consequence

      thinking aloud can produce self-contradiction requiring more context to fully understand — e.g. a patient first says he has none of the symptoms asked, then later revises to say he does get dizzy after running.
  - c. topic drift
    - i. detection difficulty

      topic drift is more common and harder to detect in spoken conversation than in text.
    - ii. example

      a "No" response actually refers to a previous question about cough, after which the topic shifts to headache.
    - iii. underlying cause

      spoken utterances are often incomplete sentences, so traditional written-text linguistic cues (punctuation marking syntactic boundaries, conjunctions signaling discourse relations) may no longer be present to help detect the shift.
- **Dialogue comprehension task**
  - a. task format

    a multi-turn symptom-checking dialogue and a query specifying a symptom with one of its attributes are given as input; the output is an answer extracted from the dialogue; a training/test sample is defined accordingly.
  - b. five clinical attributes

    (1) how long the patient has experienced the symptom, (2) activities triggering or worsening the symptom, (3) extent of seriousness, (4) frequency of occurrence, and (5) location of the symptom.
  - c. entities

    each symptom/attribute can take different linguistic expressions, termed entities.
  - d. unanswerable case

    if the queried symptom or attribute isn't mentioned in the dialogue, the groundtruth output is "No Answer," following the convention in BIBREF6.
- **Related work**
  - a. reading comprehension
    - i. large-scale QA datasets

      SQuAD and MARCO provide question-answer pairs from a wide range of written passages, covering factual answers (locations, numerical values, etc.); HotpotQA requires multi-step inference and offers numerous answer types; CoQA and QuAC are designed to mimic multi-turn information-seeking discussions.
    - ii. reasoning demands

      these tasks require contextual reasoning such as coreference resolution to capture rich linguistic patterns, pushing beyond naive lexical matching.
    - iii. neural contributions

      distributional word embeddings, contextual sequence encoding, and attention mechanisms are widely adopted in state-of-the-art comprehension models, contributing significantly to progress.
  - b. dialogue understanding vs. dialogue comprehension
    - i. active vs. underexplored areas

      dialogue language-understanding tasks like domain identification, slot filling, and user intent detection have attracted substantial research interest, but dialogue comprehension work remains limited, if it exists at all.
    - ii. data collection difficulty

      obtaining a critical mass of annotated conversation data for computational modeling is labor-intensive and time-consuming.
    - iii. human-machine/machine-machine data as a partial solution

      some work collects data from human-machine or machine-machine dialogues; since human speakers in such settings are aware of the dialogue system's limitations, or due to pre-defined user-simulator assumptions, these dialogues show fewer cases of zero anaphora, thinking aloud, and topic drift than genuine human-human spoken interaction.
  - c. NLP for healthcare
    - i. general trend

      there is emerging research interest at the intersection of machine learning and healthcare, with much of the NLP work centered on social media or online forums, partly because the web is a readily available data source.
    - ii. EHR-based work

      other work uses public sources like MIMIC electronic health records — text classification for ICD code assignment, automatic intensive/emergency prediction, and sequence-to-sequence generation of readable notes from medical/demographic records.
    - iii. mental-health dialogue work

      mental health research has focused more on analyzing dialogue, e.g. sequential modeling of audio and text to detect depression from human-machine interviews.
    - iv. gap

      few studies have examined human-human spoken conversations in healthcare settings.
- **Data preparation**
  - a. source and approval
    - i. recording source

      recordings of nurse-initiated telephone conversations with congestive heart failure patients undergoing telemonitoring post-discharge, acquired by the Health Management Unit at Changi General Hospital.
    - ii. ethics approval

      approved by the SingHealth Centralised Institutional Review Board (Protocol 1556561515); patients recruited 2014-2016 as part of routine care delivery, enrolled in the telemonitoring program with consent for anonymized research use.
  - b. dataset scale and composition

    353 conversations from 40 speakers (11 nurses, 16 patients, 13 caregivers); speakers aged 38-88, equally distributed across gender, spanning ethnic groups (55% Chinese, 17% Malay, 14% Indian, 3% Eurasian, 11% unspecified); conversations cover 11 topics (e.g. medication compliance, symptom checking, education, greeting) and 9 symptoms (e.g. chest pain, cough), totaling 41 hours.
  - c. processing pipeline

    a separate data preparation team (distinct from the analysis team, to maintain confidentiality) followed standard speech-recognition transcription guidelines, transcribing verbatim including false starts, disfluencies, mispronunciations, and private self-talk; confidential information was marked and clipped from audio and transcribed with predefined tags; conversation topics and clinical symptoms were annotated and clinically validated by certified telehealth nurses.
- **Linguistic characterization on seed data**
  - a. sampling and categorization

    1,200 turns were randomly sampled from the full 41-hour dataset and manually categorized into types (Table TABREF14, with occurrence frequency statistics); a given utterance could belong to more than one type.
  - b. inquiry types
    - i. open-ended inquiry

      inquiries about general well-being or a particular symptom, e.g. "How are you feeling?" or "Do you cough?"
    - ii. detailed inquiry

      inquiries with specific details prompting yes/no answers or clarification, e.g. "Do you cough at night?"
    - iii. multi-intent inquiry

      inquiring about more than one symptom in a single question, e.g. "Any cough, chest pain, or headache?"
    - iv. reconfirmation inquiry

      the nurse reconfirms particular details, e.g. "Really? At night?" or "Serious or mild?" — usually related to explicit or implicit coreferencing.
    - v. inquiry with transitional clauses

      a speaker repeats what the other party said, unrelated to the question's main clause, typically due to private self-talk while thinking aloud, forming a transitional clause before a new topic begins, e.g. "Chest pain... no chest pain, I see... any cough?"
  - c. response types
    - i. yes/no response

      seemingly straightforward but can cause misunderstanding if context isn't correctly interpreted, e.g. tag-question confusion ("You don't cough at night, do you?" / "Yes, yes" / "cough at night?" / "No, no cough"); when the answer is unclear, clarifying reconfirmation questions typically follow.
    - ii. detailed response

      responses containing specific symptom information, e.g. "I felt tightness in my chest."
    - iii. response with revision

      infrequent but significant for comprehension; a later response overrules an earlier one due to thinking aloud, e.g. "No dizziness, oh wait... last week I felt a bit dizzy when biking."
    - iv. response with topic drift

      the response addresses a different symptom/topic than the one inquired about, e.g. answering a headache question with "Only some chest pain at night."
    - v. response with transitional clauses

      repeats prior content, usually unrelated to critical clinical information and typically followed by topic drift, e.g. "Swelling... swelling... I don't cough at night."
- **Simulated dataset construction**
  - a. two-stage overview

    construction is divided into two stages: building templates and expression pools via linguistic analysis plus manual verification, then generating simulated training data via a proposed framework; both the templates and the framework are verified for logical correctness and clinical soundness.
  - b. template construction
    - i. abstraction procedure

      each categorized seed utterance is abstracted into a template by replacing entity phrases (e.g. "cough," "often") with placeholders (e.g. "#symptom#," "#frequency#").
    - ii. refinement

      templates are refined by linguistically trained researchers for logical correctness and injected expression diversity; since placeholder substitution doesn't alter syntactic structure, placeholders can be interchanged with various verbal expressions to enlarge the simulated training set; clinical validation was also performed by certified telehealth nurses.
    - iii. expression pool construction

      for the 9 symptoms and 5 attributes, various expressions were collected from seed data and expanded via synonym replacement; some attributes are symptom-specific (e.g. "left leg" under #location# suits swelling but not headache), so only general, symptom-agnostic expressions (e.g. "slight" under #extent#) are reused across symptoms to diversify expression.
    - iv. authorship and use

      two linguistically trained researchers built the expression pools per symptom/attribute, accounting for different paraphrasing/description types; these pools feed step (c) of the generation framework.
  - c. five-step simulated data generation framework
    - i. topic selection

      although nurses might inquire about symptoms in different orders depending on patient history, preliminary analysis showed modeling results don't differ noticeably by topic order, so topics are assumed equally likely for simplicity.
    - ii. template selection

      one inquiry template and one response template are randomly chosen per selected topic to compose a turn; to reduce underfitting, the utterance-type frequency distribution from Table TABREF14 is redistributed — types below 15% are boosted to 15% — while keeping the overall relative ranking balanced and consistent with the original table.
    - iii. enriching linguistic expressions

      placeholders in selected templates are substituted with diverse expressions from the expression pools, to characterize symptoms and their attributes.
    - iv. multi-turn dialogue state tracking
      - completion tracking: a greedy algorithm completes conversations using a "completed symptoms" list and a "to-do symptoms" list for topic tracking, alongside "completed attributes" and "to-do attributes" lists; all related attributes are iterated for each symptom.
      - termination condition: a dialogue ends only when all possible entities are exhausted, yielding a multi-turn dialogue sample that encourages the model to learn from the full discussion flow rather than a single turn, to comprehend contextual dependency.
      - length statistic: the average simulated dialogue length is 184 words, twice the average length of a real-world evaluation-set dialogue.
      - respondent role modeling: the patient-to-caregiver ratio is set to 2:1, inspired by real seed-dataset proportions; equal gender probability is assumed for both roles, with corresponding pronouns determined by the assigned role and gender.
    - v. multi-turn sample annotation

      for each multi-turn dialogue, a query is specified by a symptom and attribute; the groundtruth QA output is automatically labeled from the template generation rules, then manually verified for annotation quality; the unanswerable design from BIBREF6 is adopted — when a symptom isn't mentioned, the answer is "No Answer"; this process repeats until all logical symptom-attribute permutations are exhausted.
- **Model design**
  - a. base model

    an established bi-directional attention pointer network is used, equipped with an added answerable classifier.
  - b. architecture pipeline
    - i. embedding

      tokens in the dialogue and query are converted into embedding vectors.
    - ii. contextual encoding

      dialogue embeddings are fed to a bi-directional LSTM encoding layer, producing a sequence of contextual hidden states.
    - iii. bi-directional attention

      hidden states and query embeddings are processed by a bi-directional attention layer, fusing context-to-query and query-to-context attention information.
    - iv. modeling layers

      two subsequent bi-directional LSTM modeling layers read the attention-fused contextual sequence.
    - v. answer span prediction

      two respective linear layers with softmax functions estimate each token's probability of being the start and end of the answer span.
  - c. no-answer handling

    a special "[SEQ]" tag is added at the head of the dialogue to represent the "No answer" case, following BIBREF4's approach, paired with an answerable classifier from BIBREF25; when the queried symptom/attribute isn't mentioned, the answer span should point to "[SEQ]" and the answerable probability should be predicted as 0.
- **Implementation details**

  the model was trained via gradient backpropagation using a cross-entropy loss covering both answer-span prediction and answerable classification, optimized with Adam at a set initial learning rate; pre-trained GloVe embeddings were used; training samples were reshuffled each epoch with a set batch size; out-of-vocabulary words were replaced with a fixed random vector; L2 regularization and dropout were applied to alleviate overfitting.
- **Evaluation setup**
  - a. Base Set

    1,264 samples held out from the simulated data.
  - b. Augmented Set

    1,280 samples built by adding two out-of-distribution symptoms ("bleeding" and "cold," never seen in training) with corresponding dialogue content and queries, to the Base Set.
  - c. Real-World Set

    944 samples manually delineated from the symptom-checking portions (approximately 4 hours) of real-world dialogues and annotated as evaluation samples.
- **Results**
  - a. metrics and method

    results are reported in Table TABREF25 using exact match (EM) and F1 score (per BIBREF0's metrics), measured on token position indices to distinguish the correct answer span from plausible spans containing the same words.
  - b. training-size effect

    both EM and F1 increase with growing training sample size, with 100k identified as the optimal size in this setting.
  - c. generalization to out-of-distribution symptoms

    the best-trained model performs well on both the Base Set and the Augmented Set, indicating out-of-distribution symptoms don't degrade comprehension of existing symptoms, and reasonable answers are produced for both in- and out-of-distribution symptoms.
  - d. real-world performance

    78.23 EM score and 80.18 F1 score on the Real-World Set.
  - e. error analysis
    - i. expression sparsity

      the expression pools exclude various valid but sporadic expressions, contributing to the performance drop from simulated test sets.
    - ii. chit-chat

      nurses and patients occasionally chit-chat in the Real-World Set, which was not simulated in training; this can make conversations overly lengthy and lower information density, potentially distracting/confusing the comprehension model.
    - iii. causal-relation elaboration

      an infrequent but interesting error source arises when patients elaborate on possible causal relations between two symptoms, e.g. "My giddiness may be due to all this cough"; the authors state they are currently investigating how to close this performance gap efficiently.
- **Ablation analysis**
  - a. bi-attention ablation

    bypassing the bi-attention layer (feeding contextual hidden states and query embeddings directly to the modeling layer) degrades performance.
  - b. embedding ablation

    replacing pre-trained GloVe embeddings with randomly initialized embeddings trained from scratch also degrades performance.
  - c. magnitude

    these two ablations lead to 10% and 18% performance degradation on the Augmented Set and Real-World Set, respectively (Table TABREF27).
- **Conclusion**
  - a. summary of contributions

    the paper formulates a dialogue comprehension task motivated by the need in telehealth settings to extract key clinical information from spoken nurse-patient conversations; it analyzes linguistic characteristics of real-world human-human symptom-checking dialogues, constructs a simulated dataset from linguistically inspired and clinically validated templates, and prototypes a QA system.
  - b. demonstrated effectiveness

    the model works effectively on a simulated test set using symptoms excluded during training, and on real-world nurse-patient conversations.
  - c. ongoing/future work

    the authors are currently improving the model's dialogue comprehension capability in complex reasoning and context understanding, and also applying the QA model to summarization and virtual nurse applications.
- **Acknowledgements**

  the work was supported by Digital Health and Deep Learning funding (I2R DL2 SSF Project No: A1718g0045) and the Science and Engineering Research Council (SERC Project No: A1818g0044) at A*STAR, Singapore, using resources from the Human Language Technology unit at I2R; telehealth data acquisition was funded by the Economic Development Board (EDB) Singapore Living Lab Fund and Philips Electronics' Hospital to Home Pilot Project (EDB grant S14-1035-RF-LLF H and W); the authors also acknowledge individual colleagues at I2R and Changi General Hospital, plus Eduard Hovy, Bonnie Webber, and anonymous reviewers for feedback.
