- **Jasper: end-to-end convolutional acoustic model**
  - **Motivation**
    - a. conventional ASR pipeline

      conventional ASR systems chain several independently learned components: an acoustic model predicting context-dependent sub-phoneme states (senones), a graph mapping senones to phonemes, and a pronunciation model mapping phonemes to words.
    - b. hybrid systems

      hybrid systems combine hidden Markov models (for state dependencies) with neural networks (for state prediction).
    - c. end-to-end motivation

      newer end-to-end (E2E) systems reduce the overall complexity of the final system by collapsing this pipeline.
  - **Lineage**
    - a. prior architectures drawn on

      the work builds on time-delay neural networks (TDNN), other convolutional neural network forms, and Connectionist Temporal Classification (CTC) loss.
    - b. wav2letter inspiration

      Jasper takes direct inspiration from wav2letter, which uses 1D-convolution layers.
    - c. Liptchinsky et al. extension

      Liptchinsky et al. improved wav2letter by increasing depth to 19 convolutional layers and adding Gated Linear Units (GLU), weight normalization, and dropout.
  - **Design goal**

    by building a deeper, larger-capacity network than prior wav2letter variants, the authors aim to match or outperform non-end-to-end models on LibriSpeech and the 2000hr Fisher+Switchboard task.
  - **Design**
    - a. operator set

      Jasper's architecture contains only 1D convolution, batch normalization, ReLU, and dropout layers — operators highly optimized for training and inference on GPUs.
    - b. why ReLU + batch norm

      ReLU and batch normalization were found to outperform other activation and normalization schemes tested for convolutional ASR.
  - **Scale**
    - a. largest variant

      the largest Jasper uses 54 convolutional layers and 333M parameters.
    - b. smaller variant

      the smaller Jasper uses 34 convolutional layers and 201M parameters.
    - c. enabling mechanism

      residual connections are used to enable this level of depth; the authors investigate several residual options and propose a new topology, Dense Residual (DR).
  - **Contributions**

    the paper states it makes a set of contributions, but the itemized list is not present in the given source text (the heading is followed directly by the next section).
  - **Headline results**
    - a. LibriSpeech test-clean, LM-assisted

      integrating the best acoustic model with a Transformer-XL language model gives a new SOTA of 2.95% WER on LibriSpeech test-clean.
    - b. LibriSpeech test-other

      SOTA results among end-to-end models on LibriSpeech test-other.
    - c. other datasets

      competitive results on Wall Street Journal (WSJ) and 2000hr Fisher+Switchboard (F+S).
    - d. greedy decoding

      using only greedy decoding without a language model, Jasper achieves 3.86% WER on LibriSpeech test-clean.
- **Jasper architecture**
  - a. input features

    Jasper uses mel-filterbank features calculated from 20ms windows with 10ms overlap, and outputs a probability distribution over characters per frame.
  - b. block structure

    Jasper has a block architecture: a Jasper BxR model has B blocks, each with R sub-blocks; all sub-blocks within a block share the same number of output channels.
  - c. sub-block operations

    each sub-block applies, in sequence: a 1D-convolution, batch norm, ReLU, and dropout.
  - d. residual connection mechanics
    - i. projection step

      each block's input is connected directly into the block's last sub-block via a residual connection, first projected through a 1x1 convolution (to reconcile differing input/output channel counts), then through a batch norm layer.
    - ii. summation

      the output of this projection batch norm is added to the output of the last sub-block's own batch norm layer.
    - iii. final activation

      the sum is passed through the activation function and dropout to produce the sub-block's output.
  - e. inference-time kernel fusion

    each sub-block was designed to fuse into a single GPU kernel: dropout is dropped at inference time, batch norm fuses with the preceding convolution, ReLU clamps the result, and the residual summation is treated as a modified bias term in the fused operation.
  - f. fixed extra blocks

    all Jasper models add four extra convolutional blocks beyond the core BxR stack: one pre-processing block and three post-processing blocks.
  - g. Dense Residual (DR) variant
    - i. relation to DenseNet/DenseRNet

      Jasper DR follows DenseNet and DenseRNet in spirit, but instead of dense connections within a block, the output of a convolution block is added to the inputs of all following blocks.
    - ii. addition vs. concatenation

      DenseNet and DenseRNet concatenate the outputs of different layers; Jasper DR instead adds them, the way ResNet adds residuals — the authors find addition to be as effective as concatenation.
- **Normalization and activation study**
  - a. normalization types compared

    batch norm, weight norm, and layer norm.
  - b. ReLU variants compared

    ReLU, clipped ReLU (cReLU), and leaky ReLU (lReLU).
  - c. gated unit types compared

    gated linear units (GLU) and gated activation units (GAU).
  - d. two-stage selection process
    - i. small-model screening

      a smaller Jasper5x3 model was used first to pick the top 3 settings; layer norm with GAU performed best, followed by layer norm with ReLU, then batch norm with ReLU.
    - ii. large-model confirmation

      the top 3 settings were then tested on a larger Jasper10x4; batch norm with ReLU outperformed the others at this scale, settling the final choice of batch normalization and ReLU for the architecture.
  - e. padding/masking fixes
    - i. layer norm padding problem

      padded sequences (all sequences padded to the longest in a batch) distorted mean/variance calculations under layer norm.
    - ii. sequence masking fix

      a sequence mask was applied to exclude padding values from the mean and variance calculation, computing mean/variance over both time and channel dimensions, similar to Laurent et al.'s sequence-wise normalization.
    - iii. additional masking experiments

      masking was also applied prior to the convolution operation, and to the mean/variance calculation in batch norm.
    - iv. masking result

      masking before convolution alone gave a lower WER, but using masks for both convolution and batch norm together resulted in worse performance.
  - f. weight norm instability

    training with weight norm was found to be very unstable, leading to exploding activations.
- **Residual connections**
  - a. necessity for deep models

    for models deeper than Jasper 5x3, residual connections were consistently observed to be necessary for training to converge.
  - b. variants investigated

    beyond simple residual and Dense Residual, the authors investigated DenseNet- and DenseRNet-style variants; DenseNet connects each sub-block's output to the inputs of following sub-blocks within a block, while DenseRNet (like Dense Residual) connects each block's output to the inputs of all following blocks.
  - c. addition vs. concatenation

    DenseNet and DenseRNet combine connections via concatenation; Residual and Dense Residual use addition instead.
  - d. comparative performance

    Dense Residual and DenseRNet performed similarly, each better on different subsets of LibriSpeech.
  - e. final choice: Dense Residual

    Dense Residual was chosen for subsequent experiments because, unlike DenseNet/DenseRNet, its addition-based growth factor doesn't need retuning for deeper models — it simply repeats a sub-block, whereas concatenation-based growth requires tuning.
- **Language model integration**
  - a. role of a language model

    a language model is a probability distribution over symbol sequences that assigns higher probability to more likely sequences; LMs are used to condition beam search, where candidates are evaluated using both acoustic and LM scores.
  - b. prior art

    traditional N-gram LMs have recently been augmented with neural LMs in other work.
  - c. models tried

    the authors experiment with statistical N-gram language models and neural Transformer-XL models.
  - d. two-stage decoding pipeline
    - i. candidate generation

      acoustic scores plus a word-level N-gram LM generate a candidate list via beam search with width 2048.
    - ii. rescoring

      an external Transformer-XL LM then rescores the final candidate list.
  - e. training independence

    all language models were trained on datasets independent from the acoustic models.
  - f. perplexity-WER correlation

    a strong correlation was observed between neural LM quality (measured by perplexity) and WER.
- **NovoGrad optimizer**
  - a. relation to Adam

    NovoGrad is an optimizer similar to Adam, except its second moments are computed per layer instead of per weight.
  - b. benefits over Adam

    compared to Adam, NovoGrad reduces memory consumption and was found to be more numerically stable.
  - c. update mechanics
    - i. gradient computation

      at each step, NovoGrad computes the stochastic gradient following the regular forward-backward pass.
    - ii. per-layer second moment

      a second-order moment is then computed for each layer, similar to ND-Adam.
    - iii. gradient rescaling

      the second-order moment is used to rescale gradients before calculating the first-order moment.
    - iv. optional weight decay

      if L2-regularization is used, a weight decay term is added to the rescaled gradient, as in AdamW.
    - v. weight update

      new weights are finally computed using the learning rate.
  - d. measured gain

    switching from SGD with momentum to NovoGrad decreased WER on dev-clean LibriSpeech from 4.00% to 3.64% (a 9% relative improvement) for Jasper DR 10x5.
  - e. future work note

    the authors state they will further analyze NovoGrad in forthcoming work.
- **Results**
  - a. training setup
    - i. regularization

      dropout and weight decay are used as regularization in all experiments.
    - ii. speed perturbation

      fixed ±10% speed perturbation is used for LibriSpeech; a random factor between -10% and 10% is applied per utterance for WSJ and Hub5'00.
    - iii. training infrastructure

      all models are trained on NVIDIA DGX-1 in mixed precision, using the OpenSeq2Seq toolkit.
    - iv. release note

      source code, training configurations, and pretrained models are made available.
  - b. read speech
    - i. datasets

      evaluated on two read-speech datasets: LibriSpeech and Wall Street Journal (WSJ).
    - ii. LibriSpeech training

      Jasper DR 10x5 trained with the NovoGrad optimizer for 400 epochs achieves SOTA performance on test-clean and SOTA among end-to-end models on test-other.
    - iii. WSJ training

      a smaller Jasper 10x3 model was trained with SGD with momentum for 400 epochs on a combined 80-hour WSJ dataset (LDC93S6A / WSJ0 and LDC94S13A / WSJ1).
  - c. conversational speech
    - i. dataset

      evaluated on the Hub5 Year 2000 (Hub5'00) evaluation (LDC2002S09, LDC2005S13), split into Switchboard (SWB) and Callhome (CHM) subsets.
    - ii. training data

      acoustic and language models were trained on the 2000hr Fisher+Switchboard training data (LDC2004S13, LDC2005S13, LDC97S62).
    - iii. training regime

      Jasper DR 10x5 was trained with SGD with momentum for 50 epochs, compared against other models trained on the same data.
    - iv. outcome

      good results were obtained on Switchboard, but Callhome remains a harder subset requiring further work.
- **Conclusion**
  - a. summary of approach

    the paper presents a new family of end-to-end neural architectures for speech recognition, inspired by wav2letter's convolutional approach, built as a deep and scalable model requiring a well-designed residual topology, effective regularization, and a strong optimizer.
  - b. outcome

    the architecture studies demonstrate that a combination of standard components leads to SOTA results on LibriSpeech and competitive results on other benchmarks.
  - c. efficiency claim

    the Jasper architecture is described as highly efficient for training and inference.
  - d. positioning as baseline

    Jasper is presented as a good baseline on top of which to explore more sophisticated regularization, data augmentation, loss functions, language models, and optimization strategies.
  - e. open question

    the authors are interested in whether the approach can continue to scale to deeper models and larger datasets.
