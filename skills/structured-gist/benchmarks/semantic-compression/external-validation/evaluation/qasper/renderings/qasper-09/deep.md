- **Hierarchical Transformers for long document classification**
  - **Problem**
    - a. BERT's strength and limitation

      BERT achieves state-of-the-art performance on several language understanding tasks (question answering, natural language inference, semantic similarity, sentiment analysis, among others), but Transformers generally can consume only a limited context of symbols, hindering classification of long sequences.
    - b. relevant long-sequence tasks

      topic identification of spoken conversations and call-center customer satisfaction (CSAT) prediction are of particular interest as long-sequence NLP tasks.
    - c. call transcript characteristics

      call center conversations, though often short and to the point, can involve agents resolving complex issues, with calls sometimes lasting an hour or more; transcribed via ASR, these transcripts sometimes exceed 5000 words.
    - d. temporal-information motivation

      temporal information can matter for tasks like CSAT — e.g. a customer angry early in a call may end up satisfied once the issue is resolved — so bag-of-words or other temporally-agnostic models may be poorly suited, motivating a model like BERT.
  - **Method**
    - a. core idea

      the input text sequence is split into shorter segments, each represented via BERT, then classified using either a recurrent LSTM network (Recurrence over BERT, RoBERT) or another Transformer (Transformer over BERT, ToBERT).
    - b. naming rationale

      because these models introduce a hierarchy of representations (segment-wise then document-wise), they are called Hierarchical Transformers.
    - c. novelty claim

      to the authors' knowledge, no prior attempt has applied the Transformer architecture to classification of such long sequences.
  - **Novel contributions**
    - a. two BERT extensions

      RoBERT and ToBERT enable BERT's application to long-text classification via segmentation plus an additional layer over segment representations.
    - b. Fisher SOTA

      state-of-the-art results on the Fisher topic classification task.
    - c. CSAT improvement

      significant improvement on the CSAT prediction task over the MS-CNN model.
- **Related work**
  - a. dimensionality-reduction approaches

    several algorithms (RBM, autoencoders, subspace multinomial models/SMM) obtain a low-dimensional representation of documents from a simple bag-of-words representation, then classify with simple linear classifiers.
  - b. hierarchical attention networks

    BIBREF14 uses hierarchical attention networks for document classification, evaluated on datasets averaging around 150 words.
  - c. character-level CNNs

    explored in BIBREF15, but described as prohibitive for very long documents.
  - d. arXiv block-sampling method

    BIBREF16 classifies arXiv papers by sampling random blocks of words and using them jointly for classification instead of the full document; this may work because arXiv papers are usually coherent, well-written, and on a well-defined topic, but the authors argue it may not work well on spoken conversations, since a random word block often doesn't represent the whole conversation's topic.
  - e. CSAT prediction prior work

    several works address predicting customer satisfaction, mostly applying logistic regression, SVM, or CNN to various representations.
  - f. BERT applied to shorter documents

    BIBREF17 uses BERT for document classification, but the average document length there is below BERT's 512-token maximum.
  - g. TransformerXL

    an extension to the Transformer architecture for better handling of long inputs in language modelling, relying on the model's auto-regressive property — a property not present in this paper's classification tasks.
- **BERT background**
  - a. architectural building blocks

    BERT is built on the Transformer architecture, using self-attention, feed-forward layers, residual connections, and layer normalization as its main components.
  - b. pretraining objectives
    - i. masked language modelling

      some words in a sentence are masked and the model predicts them from context — distinct from the typical autoregressive language-model training objective.
    - ii. next sentence prediction

      given two input sequences, the model decides whether the second is the next sentence following the first.
  - c. established fine-tuning procedure

    BERT has been shown to beat the state of the art on 11 tasks with no architectural modification beyond adding a task-specific output layer; this paper follows the same procedure for its tasks.
  - d. representations extracted

    two kinds of representation are obtained from BERT: the pooled output from the last transformer block (denoted H), and posterior probabilities (denoted P).
  - e. model size variants

    BERT-Base and BERT-Large differ in parameters such as number of transformer blocks and self-attention heads; BERT-Base has 110M parameters and BERT-Large has 340M; this work uses BERT-Base for faster training/experimentation, though the methods are stated to be applicable to BERT-Large too.
  - f. limitations for long sequences
    - i. quadratic self-attention cost

      the self-attention layer has O(n²) complexity in sequence length n.
    - ii. positional embedding limitation

      BERT uses learned positional embeddings, meaning it likely cannot generalize to positions beyond those seen during training.
  - g. fine-tuning variants investigated

    to study fine-tuning's effect on performance, the paper compares pre-trained BERT weights, weights fine-tuned per-segment on the task-specific dataset (preserving the original document label but fine-tuning on each segment separately), and using the fine-tuned segment-level BERT predictions directly as inputs to the next layer.
- **Recurrence over BERT (RoBERT)**
  - a. segmentation

    the input sequence is split into fixed-size segments with overlap, since BERT is limited to a particular input length; H or P is obtained from BERT for each segment.
  - b. aggregation

    segment-level representations are stacked into a sequence and fed into a small (100-dimensional) LSTM layer, whose output serves as the document embedding.
  - c. classification head

    two fully connected layers are applied: a ReLU layer (30-dimensional) followed by a softmax layer (dimensionality equal to the number of classes), producing the final prediction.
  - d. complexity benefit

    this reduces BERT's computational complexity to O(n/k · k²) = O(nk) for RoBERT, where k is the segment size (the LSTM component adds only negligible linear O(k) complexity); the positional-embedding generalization issue is also no longer relevant.
- **Transformer over BERT (ToBERT)**
  - a. motivation

    Transformers' advantage over recurrent networks is their ability to effectively capture long-distance relationships between words, motivating experimentation with replacing the LSTM recurrent layer with a small Transformer model (2 layers of the transformer building block, containing self-attention, fully connected layers, etc.).
  - b. positional embeddings variant

    to investigate whether preserving input sequence order matters, a ToBERT variant learns positional embeddings at the segment-level representations, though this limits it to sequence lengths seen during training.
  - c. complexity tradeoff

    ToBERT's O(n²/k²) complexity is asymptotically inferior to RoBERT's, since the top-level Transformer again has quadratic complexity, this time in the number of segments; however, since n/k is much smaller than n in practice, no performance or memory issues were observed on the datasets used.
- **Experiments**
  - a. three datasets evaluated
    - i. CSAT

      CSAT dataset for CSAT prediction, consisting of spoken transcripts obtained via ASR.
    - ii. 20 newsgroups

      used for a topic identification task, consisting of written text.
    - iii. Fisher

      Fisher Phase 1 corpus, used for a topic identification task, consisting of manually transcribed spoken conversations.
  - b. CSAT dataset details
    - i. source and labeling

      US English telephone speech from call centers; customers on each call rated their experience with the agent on a 1-9 scale (9 = extremely satisfied, 1 = extremely dissatisfied).
    - ii. label quantization

      given the skewed rating distribution (shown in a histogram, Fig. FIGREF16), ratings are binarized at 4.5 (satisfied above, dissatisfied below), which also helps balance the dataset.
    - iii. dataset size/splits

      4331 calls total, split into 2866 for training, 362 for validation, and 1103 for testing.
    - iv. ASR system used

      transcripts were obtained via an ASR system using a TDNN-LSTM acoustic model trained on Fisher and Switchboard with a lattice-free maximum mutual information criterion; word error rates with four-gram language models were 9.2% (Switchboard) and 17.3% (CallHome) on the Eval2000 dataset.
  - c. 20 newsgroups details
    - i. general description

      one of the frequently used text classification/clustering datasets, containing approximately 20,000 English documents across 20 topics, with a standard split of 11314 training and 7532 test documents.
    - ii. this paper's split

      90% of the training documents are used for training and the remaining 10% for validation.
    - iii. vocabulary

      a 53160-word vocabulary from the dataset's website is used, for fair comparison with other publications.
  - d. Fisher details
    - i. general description

      Fisher Phase 1 US English corpus is commonly used for automatic speech recognition research; here it is used for topic identification, following BIBREF3's setup, consisting of 10-minute two-person telephone conversations discussing a given topic.
    - ii. splits

      the same training/test split as BIBREF3 is used (1374 training, 1372 test documents); 10% of the training dataset is used for validation, with the remaining 90% for actual training.
    - iii. topic count

      the dataset contains 40 topics.
  - e. dataset length statistics
    - i. relative lengths

      Table TABREF22 shows Fisher's average document length is much higher than that of 20 newsgroups and CSAT.
    - ii. cumulative length distribution

      Fig. FIGREF21 shows almost all Fisher documents exceed 1000 words; over 50% of CSAT documents exceed 500 words, versus only about 10% of 20newsgroups documents; a small number of CSAT and 20newsgroups documents exceed 5000 words.
  - f. architecture and training details
    - i. segmentation parameters

      documents are split into 200-token segments with a 50-token shift to extract BERT features.
    - ii. RoBERT training

      the LSTM model is trained to minimize cross-entropy loss with the Adam optimizer; initial learning rate 0.001, reduced by a factor of 0.95 if validation loss doesn't decrease for 3 epochs.
    - iii. ToBERT training

      the Transformer is trained with the default BERT version of the Adam optimizer, initial learning rate 5e-5.
    - iv. evaluation protocol

      accuracy is reported for all experiments; the model with the best validation accuracy is selected to compute test accuracy; to account for non-determinism in some TensorFlow GPU operations, accuracy is averaged over 5 runs.
- **Results**
  - a. pre-trained BERT features
    - i. table and feature choice

      Table TABREF25 presents results using pre-trained BERT features, extracted from the pooled output of the final transformer block, since these were shown to work well for most tasks in prior work.
    - ii. finding

      pre-trained (non-fine-tuned) BERT features lead to sub-par performance; ToBERT exploits these features better than RoBERT and converges faster.
  - b. fine-tuned BERT features
    - i. table

      Table TABREF26 shows results using features extracted after fine-tuning BERT on the task datasets.
    - ii. overall effect

      significant improvements are observed compared to pre-trained features.
    - iii. ToBERT vs. RoBERT

      ToBERT outperforms RoBERT on Fisher (by 13.63%) and 20newsgroups (by 0.81%); on CSAT, ToBERT performs slightly worse than RoBERT, though the difference is not statistically significant given the small dataset size.
  - c. using fine-tuned BERT predictions directly
    - i. table and setup

      Table TABREF27 presents results using fine-tuned BERT predictions (rather than pooled output); for each document, segment-wise predictions can be combined into a final prediction in three ways.
    - ii. three aggregation methods

      average all segment-wise predictions and take the most probable class; take the most frequently predicted class; or train a classification model (i.e. RoBERT/ToBERT).
    - iii. finding on averaging/majority-vote

      simple averaging or most-frequent-class aggregation is competitive for CSAT and 20newsgroups but not for Fisher.
    - iv. hypothesis for the pattern

      the improvement from RoBERT/ToBERT over simple averaging/majority-vote is believed to be proportional to the fraction of long documents in the dataset — CSAT and 20newsgroups have significantly shorter average documents than Fisher (per Fig. FIGREF21); the larger Fisher improvement may also relate to less-confident per-segment BERT predictions, since Fisher has 40 classes.
    - v. length-range analysis

      Fig. FIGREF31 compares average voting and ToBERT across document-length ranges for Fisher, using fine-tuned BERT segment-level predictions (P); ToBERT outperforms average voting in every length interval.
    - vi. SOTA claim

      to the authors' knowledge, this is a state-of-the-art result on the Fisher dataset.
  - d. effect of position embeddings
    - i. table

      Table TABREF32 presents the effect of position embeddings on model performance.
    - ii. finding

      position embeddings do not significantly affect performance for Fisher and 20newsgroups, but help slightly for CSAT (an absolute 0.64% F1-score improvement).
    - iii. interpretation

      Fisher and 20newsgroups are topic-identification tasks where the topic doesn't change much throughout the document; CSAT can vary during the call, so assuming the sequential nature of the transcript is irrelevant may lead to wrong conclusions there.
  - e. comparison with prior work
    - i. table

      Table TABREF33 compares results with previous works.
    - ii. finding

      ToBERT outperforms CNN-based experiments by a significant margin on CSAT and Fisher; for CSAT, the baseline is multi-scale CNN (MS-CNN), chosen for its strong results on Fisher and 20newsgroups, with the setup replicated from BIBREF5 for comparison.
    - iii. 20 newsgroups result

      the paper's 20 newsgroups result is 0.6% worse than the state of the art.
- **Conclusions**
  - a. summary of methods and tasks

    two methods for long-document classification using BERT — RoBERT and ToBERT — are presented and evaluated on two classification tasks (customer satisfaction prediction and topic identification) using three datasets (CSAT, 20newsgroups, Fisher).
  - b. ToBERT vs. RoBERT

    ToBERT outperforms RoBERT on both pre-trained and fine-tuned BERT features for all tasks.
  - c. fine-tuning effect

    fine-tuned BERT performs better than pre-trained BERT.
  - d. improvement over simple baselines

    both RoBERT and ToBERT improve on simple baselines of averaging or taking the most frequent segment-wise prediction for long documents.
  - e. position embeddings effect

    position embeddings did not significantly affect model performance overall, but slightly improved CSAT accuracy.
  - f. best results

    the best results were obtained on the Fisher dataset, with good improvements for the CSAT task compared to the CNN baseline.
  - g. length-correlated benefit

    it is noted that the longer the average input for a given task, the larger the improvement observed relative to the baseline for that task.
  - h. overall claim

    the results confirm that both RoBERT and ToBERT can be used for long sequences with competitive performance and a quick fine-tuning procedure.
  - i. future work

    future work will focus on training models on long documents directly, i.e. in an end-to-end manner.
