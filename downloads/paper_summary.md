

# 歸檔時間: 2026-04-27 18:41:32
### 文獻名稱
Long-tail Internet photo reconstruction

### 文獻中文名稱
長尾網路照片重建

- 論文來源 URL: https://arxiv.org/abs/2604.22714
- 抓取時間：2026-04-27 10:31 UTC

### 一句話核心
針對網路照片中大量冷門地標，提出新資料集與採樣策略，讓 3D 重建模型在稀疏影像下也能穩定運作。

### 30 秒看懂這篇論文
- 解決什麼問題：現有模型在稀疏、雜亂的網路照片中常無法重建出穩定幾何。
- 方法是什麼：使用過濾後的優質重建資料模擬長尾情況，並用「稀疏感知採樣」訓練模型。
- 結果如何：在極端稀疏與雙胞胎場景（相似建築）上表現大幅改進，同時保留對標準資料集的泛化能力。

### 先備知識
- 3D 重建（3D reconstruction）：從 2D 照片還原出三維場景。
- SfM（Structure-from-Motion）：傳統從多張照片推算相機位置與 3D 點的技術。
- 長尾（long-tail）：資料分佈中少見但實際上很常見的案例。

### 重要名詞
1. **長尾（long-tail）**：照片資料裡，熱門地標影像多，冷門地標影像少，這種分佈叫長尾。
2. **雙胞胎問題（doppelganger）**：相似建築的照片被錯誤當成同一場景，導致重建混亂。
3. **稀疏感知採樣（sparsity-aware sampling）**：刻意挑選稀疏但具多視角的照片來訓練，讓模型學得更 robust。

### 研究動機
- 背景：網路照片多數集中在幾個熱門地標，大部分真實影像都很稀疏。
- 痛點：現行模型在稀疏照片上表現差，無法處理長尾場景。
- 目標：透過模擬訓練與新資料集，讓模型在稀疏與雜亂的網路照片也能重建。

### 方法流程
1. 過濾與消歧：從 MegaScenes 挑選穩定重建的場景，排除動態內容與雙胞胎問題。
2. 深度細化：運用多視角立體（MVS）與單眼深度先驗，產生高品質深度圖。
3. 模擬長尾：用稀疏感知採樣從資料集中抽取稀疏但有覆蓋度的照片子集。
4. 微調模型：用處理過的 MD-X 資料集訓練 VGGT 與 π³ 等基礎模型。

### 圖表導讀
- 圖表重點：圖 6 展示在真實長尾場景上，微調模型與傳統 SfM 或預訓練模型的對比。
- 怎麼看：同一場景中，底部幾張稀疏照片的重建結果，微調模型明顯更完整且無碎片。
- 新手重點：即使只有幾張角度不一的照片，也能還原出正確的三維場景。

### 理解檢查
Q: 這篇論文最主要想解決什麼問題？
A. 提高 3D 重建模型在稀疏、雜亂的網路照片上的表現
B. 開發一種新的物體識別演算法
C. 降低電腦視覺模型的計算成本
D. 設計更快速的影像壓縮技術
答案：A
解釋：論文聚焦於長尾場景下的 3D 重建挑戰，並透過資料集與採樣策略來提升模型的泛化性。

### 延伸閱讀
1. **DUSt3R**：從一對圖片預測 3D 點雲的 feed-forward 模型，這篇是它的前驅工作。
2. **VGGT**：能同時預測相機參數、深度與點雲的 Transformer 模型，本文在其上微調。
3. **MegaDepth**：早期用於學習單眼深度預測的大規模 3D 資料集，本文是其進階版 MD-X。


# 歸檔時間: 2026-04-27 19:03:08
# 今日待處理論文任務

### 一句話核心
尚未填寫核心摘要

## 文獻名稱
Are Natural-Domain Foundation Models Effective for Accelerated Cardiac MRI Reconstruction ?

- URL: https://arxiv.org/abs/2604.22557
- ID: 2604.22557
### 論文內容:

## 1 Introduction

Cardiovascular disease continues to be the leading cause of mortality worldwide, underscoring the importance of accurate and non-invasive imaging for early diagnosis and monitoring [[38](#bib.bib1 "Fill the k-space and refine the image: prompting for dynamic and multi-contrast mri reconstruction")]. Cardiac magnetic resonance (CMR) imaging has emerged as a powerful tool due to its ability to provide high-resolution assessment of cardiac anatomy, function, and tissue properties without the use of ionizing radiation [[21](#bib.bib2 "The state-of-the-art in cardiac mri reconstruction: results of the cmrxrecon challenge in miccai 2023"), [11](#bib.bib3 "Simultaneous multi-parametric acquisition and reconstruction techniques in cardiac magnetic resonance imaging: basic concepts and status of clinical development")].

Despite its clinical benefits, MRI acquisition is inherently slow because k-space measurements must be collected sequentially during the scan. Long acquisition times can lead to patient discomfort and motion artifacts [[39](#bib.bib4 "Recurrent variational network: a deep learning inverse problem solver applied to the task of accelerated mri reconstruction")]. Accelerated MRI addresses this challenge by undersampling k-space to shorten scan duration; however, reconstructing images from such incomplete measurements is an ill-posed inverse problem (i.e. there are fewer measurements than unknowns) [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction")] that requires strong prior information.

In recent years, deep learning–based reconstruction approaches have emerged as a powerful solution to this challenge [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction"), [26](#bib.bib6 "Deep learning techniques for inverse problems in imaging")]. In particular, unrolled networks have achieved state-of-the-art performance [[38](#bib.bib1 "Fill the k-space and refine the image: prompting for dynamic and multi-contrast mri reconstruction")] by combining physics-based data consistency with learned image priors, effectively integrating the MRI acquisition model with data-driven representations. However, these conventional deep learning models are typically designed for specific tasks and often require substantial retraining or fine-tuning when deployed in new settings [[30](#bib.bib8 "Foundation models in medical image analysis: a systematic review and meta-analysis")]. Moreover, their clinical applicability is frequently challenged by domain shifts arising from variations in acquisition protocols, imaging settings, scanner hardware, and anatomical differences across patient populations [[8](#bib.bib12 "Zero-shot domain generalization of foundational models for 3d medical image segmentation: an experimental study")]. These limitations highlight a key challenge: how to develop reconstruction methods that generalize reliably across diverse settings.

More recently, the broader deep learning community has increasingly shifted toward large-scale foundation models, which are pretrained on extensive datasets and exhibit strong generalization across tasks and domains [[15](#bib.bib7 "Are natural domain foundation models useful for medical image classification? in 2024 ieee/cvf winter conference on applications of computer vision (wacv). waikoloa, hi, usa: ieee;[cited 2024 aug 27]. 7619–7628"), [3](#bib.bib9 "Evaluating general purpose vision foundation models for medical image analysis: an experimental study of dinov2 on radiology benchmarks")]. Their success has been particularly transformative in natural language processing [[18](#bib.bib10 "BART: denoising sequence-to-sequence pre-training for natural language generation, translation, and comprehension"), [29](#bib.bib11 "Improving language understanding by generative pre-training"), [4](#bib.bib13 "On the opportunities and risks of foundation models")], and has recently been extended to computer vision and medical imaging [[28](#bib.bib14 "Learning transferable visual models from natural language supervision"), [27](#bib.bib15 "Dinov2: learning robust visual features without supervision"), [17](#bib.bib16 "Segment anything"), [41](#bib.bib20 "Biomedclip: a multimodal biomedical foundation model pretrained from fifteen million scientific image-text pairs"), [5](#bib.bib19 "Universeg: universal medical image segmentation"), [36](#bib.bib17 "Medclip: contrastive learning from unpaired medical images and text"), [22](#bib.bib18 "Segment anything in medical images")]. By learning rich, transferable representations from large-scale data, these models enable strong performance even in low-data or zero-shot regimes, reducing the need for task-specific supervision. This paradigm shift suggests a promising alternative to highly specialized architectures: leveraging pretrained models as general-purpose priors.

However, applying foundation models to medical imaging, and in particular to physics-based inverse problems such as MRI reconstruction–remains largely unexplored. A key challenge lies in the domain gap between natural images used for large-scale pretraining and medical imaging data. While medical imaging is often constrained by limited annotated data due to privacy and acquisition costs [[15](#bib.bib7 "Are natural domain foundation models useful for medical image classification? in 2024 ieee/cvf winter conference on applications of computer vision (wacv). waikoloa, hi, usa: ieee;[cited 2024 aug 27]. 7619–7628"), [23](#bib.bib22 "What makes transfer learning work for medical images: feature reuse & other factors"), [24](#bib.bib21 "Pretrained vits yield versatile representations for medical images")], making it well-suited for transfer learning, it is unclear whether representations learned from natural images can effectively transfer to this fundamentally different domain.

These challenges motivate a shift in perspective: rather than designing increasingly task-specific reconstruction architectures, we investigate whether the transferable representations learned by foundation models can serve as effective priors for accelerated MRI reconstruction.

Building on this perspective, we investigate whether frozen vision foundation models can serve as effective priors for physics-based MRI reconstruction, and compare natural-image-pretrained models with domain-specific counterparts such as BiomedCLIP [[41](#bib.bib20 "Biomedclip: a multimodal biomedical foundation model pretrained from fifteen million scientific image-text pairs")]. We propose an unrolled reconstruction framework that integrates pretrained visual encoders, such as CLIP [[28](#bib.bib14 "Learning transferable visual models from natural language supervision")], DINOv2 [[27](#bib.bib15 "Dinov2: learning robust visual features without supervision")], and BiomedCLIP [[41](#bib.bib20 "Biomedclip: a multimodal biomedical foundation model pretrained from fifteen million scientific image-text pairs")], within each cascade of the reconstruction pipeline. The foundation models remain frozen during training and provide feature representations that guide iterative refinement, while data-consistency operations enforce fidelity to the acquired k-space measurements.

Through extensive experiments on the CMRxRecon 2023 dataset [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")], we observe that task-specific reconstruction models, such as E2E-VarNet [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], achieve superior performance in standard in-distribution settings, as expected due to their end-to-end optimization on domain-specific MRI data. However, a markedly different trend emerges under more challenging conditions. In cross-domain evaluations and at higher acceleration factors, corresponding to increasingly ill-posed reconstruction problems, the performance gap between the two approaches narrows substantially. In these regimes, foundation-model-based reconstructions become competitive and, in some cases, surpass task-specific baseline. We further observe that natural-image-pretrained models, such as CLIP, learn highly transferable structural representations, while domain-specific pretraining (BiomedCLIP) provides modest additional gains in more ill-posed regimes.

These findings reveal a regime-dependent trade-off: while fully supervised reconstruction network excel when sufficient domain-specific data is available, pretrained foundation models provide more robust and transferable priors under distribution shifts. Overall, this suggests that large-scale visual pretraining captures structural representations that generalize beyond natural images and can be effectively leveraged for medical image reconstruction, particularly in challenging, cross-domain settings.

In summary, our main contributions are:

* •

  To the best of our knowledge, we present one of the first studies investigating frozen vision foundation models as priors for physics-based MRI reconstruction. We introduce an unrolled reconstruction framework that integrates pretrained encoders (CLIP, DINOv2, BiomedCLIP) within each cascade, and compare domain-specific (BiomedCLIP) and natural-image-pretrained models.
* •

  We evaluate performance across both in-distribution and challenging cross-domain settings, revealing a regime-dependent behavior in which task-specific model dominate under standard conditions, while foundation-model-based approaches become increasingly competitive as reconstruction difficulty and domain shift increase.
* •

  We show that large-scale pretrained visual representations, despite being learned from natural images, capture transferable structural priors that can generalize to MRI reconstruction across anatomically distinct domains.

## 2 Background and Related Work

#### Inverse Problem Modeling of Accelerated MRI Reconstruction.

Magnetic resonance imaging (MRI) acquires measurements of the underlying anatomy in the frequency domain, known as k-space. During acquisition, multiple receiver coils are used, each with a distinct spatial sensitivity profile [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction")]. Let x∗∈ℂnx^{\ast}\in\mathbb{C}^{n} denote the target image. The measurement from the ii-th coil is given by

|  |  |  |  |
| --- | --- | --- | --- |
|  | ki=ℱ​(Si​x∗)+zi,i=1,…,N,k\_{i}=\mathcal{F}(S\_{i}x^{\ast})+z\_{i},\quad i=1,\dots,N, |  | (1) |

where SiS\_{i} denotes the coil sensitivity map, ℱ\mathcal{F} the Fourier transform, and ziz\_{i} measurement noise. Collectively, measurements across all coils are denoted by k=(k1,…,kN)k=(k\_{1},\dots,k\_{N}).

To accelerate acquisition, only a subset of k-space is sampled using an undersampling mask, yielding

|  |  |  |  |
| --- | --- | --- | --- |
|  | k~i=M​ki,i=1,…,N,\tilde{k}\_{i}=Mk\_{i},\quad i=1,\dots,N, |  | (2) |

where MM is a binary sampling operator. The forward model can thus be written compactly as k~=𝒜​(x∗)\tilde{k}=\mathcal{A}(x^{\ast}), where 𝒜​(⋅)\mathcal{A}(\cdot) represents the undersampled multi-coil acquisition process.

Recovering x∗x^{\ast} from k~\tilde{k} is an ill-posed inverse problem due to insufficient measurements. Classical approaches address this by incorporating prior knowledge, such as sparsity in a transform domain, leading to compressed sensing formulations [[6](#bib.bib23 "Stable signal recovery from incomplete and inaccurate measurements"), [10](#bib.bib24 "Compressed sensing"), [20](#bib.bib25 "Compressed sensing mri")]:

|  |  |  |  |
| --- | --- | --- | --- |
|  | x^=arg⁡minx⁡‖𝒜​(x)−k~‖2+ℛ​(x),\hat{x}=\arg\min\_{x}\;\|\mathcal{A}(x)-\tilde{k}\|^{2}+\mathcal{R}(x), |  | (3) |

where ℛ​(⋅)\mathcal{R}(\cdot) encodes prior information. In modern approaches, this prior is learned directly from data using deep neural networks, forming the basis of learning-based MRI reconstruction methods.

#### Deep Learning for Accelerated MRI Reconstruction.

Deep learning has become the dominant paradigm for accelerated MRI reconstruction, with models learning data-driven image priors from large-scale datasets. Among these, unrolled networks achieve state-of-the-art performance by modeling reconstruction as a sequence of cascades, each corresponding to an iteration of an optimization algorithm [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction"), [38](#bib.bib1 "Fill the k-space and refine the image: prompting for dynamic and multi-contrast mri reconstruction"), [32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")]. This formulation enables tight integration of MRI acquisition physics, particularly k-space undersampling, with learned image-domain priors, yielding iterative refinement schemes that progressively improve reconstruction quality. A prominent and widely adopted example is the End-to-End Variational Network (E2E-VarNet) [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], which has established itself as a strong state-of-the-art baseline on benchmarks such as fastMRI [[40](#bib.bib29 "FastMRI: an open dataset and benchmarks for accelerated mri"), [12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction")]. Owing to its effectiveness and generality, E2E-VarNet has become a foundational architecture in MRI reconstruction, with many subsequent methods building upon its design.

#### Foundation Models.

Foundation models have significantly advanced transfer learning, enabling pretrained models to generalize across diverse tasks [[15](#bib.bib7 "Are natural domain foundation models useful for medical image classification? in 2024 ieee/cvf winter conference on applications of computer vision (wacv). waikoloa, hi, usa: ieee;[cited 2024 aug 27]. 7619–7628")]. In computer vision, CLIP [[28](#bib.bib14 "Learning transferable visual models from natural language supervision")] has gained widespread attention for learning aligned image–text representations via contrastive learning, supporting strong performance across a range of downstream tasks [[42](#bib.bib30 "CLIP in medical imaging: a survey")]. Recent work has explored its use in medical imaging, showing that pretrained visual features can rival or even surpass domain-specific models in certain clinical settings [[36](#bib.bib17 "Medclip: contrastive learning from unpaired medical images and text"), [25](#bib.bib31 "Radiological reports improve pre-training for localized imaging tasks on chest x-rays"), [1](#bib.bib32 "One-shot localization and segmentation of medical images with foundation models")]. To bridge the domain gap, BiomedCLIP [[41](#bib.bib20 "Biomedclip: a multimodal biomedical foundation model pretrained from fifteen million scientific image-text pairs")] extends CLIP to the biomedical domain using curated image–text pairs, achieving state-of-the-art results on multiple medical benchmarks. Similarly, self-supervised vision transformers such as DINOv2 [[27](#bib.bib15 "Dinov2: learning robust visual features without supervision")] learn robust and transferable representations without manual annotations, achieving strong performance across diverse vision tasks [[31](#bib.bib33 "General purpose image encoder dinov2 for medical image registration"), [3](#bib.bib9 "Evaluating general purpose vision foundation models for medical image analysis: an experimental study of dinov2 on radiology benchmarks")]. Despite these advances, existing work primarily focuses on high-level vision tasks. The role of foundation models in physics-based inverse problems, such as MRI reconstruction, remains largely unexplored.

## 3 Methodology

The primary objective of this work is to evaluate the effectiveness of vision foundation models in the context of MRI reconstruction. In particular, we aim to assess whether features learned from large-scale pretraining, primarily on natural images–can serve as transferable priors for reconstructing undersampled MRI data.
To this end, we propose an unrolled reconstruction framework that integrates pretrained vision foundation models within a physics-based MRI reconstruction pipeline. Given undersampled multi-coil k-space measurements, the objective is to recover an image that is both consistent with the acquired data and guided by informative structural priors. The reconstruction is modeled as a sequence of cascades, each comprising a data-consistency step and a learned refinement module.

Unlike conventional approaches that learn priors solely from task-specific MRI data, our method incorporates frozen visual encoders–such as CLIP [[28](#bib.bib14 "Learning transferable visual models from natural language supervision")], DINOv2 [[27](#bib.bib15 "Dinov2: learning robust visual features without supervision")], and BiomedCLIP [[41](#bib.bib20 "Biomedclip: a multimodal biomedical foundation model pretrained from fifteen million scientific image-text pairs")], within each cascade. These encoders extract feature representations from intermediate reconstructions, which are used to guide iterative refinement. This design enables the model to leverage large-scale pretrained knowledge while maintaining fidelity to the underlying acquisition physics.

#### Foundation Model Encoders.

All encoders are transformer-based models pretrained on large-scale datasets using self-supervised or multimodal objectives. We select representative models spanning both natural-image and medical-domain pretraining to study the impact of pretraining data on reconstruction performance. For all models, we use the ViT-B backbone for consistency across experiments.

* •

  CLIP (Contrastive Language-Image Pre-training) [[28](#bib.bib14 "Learning transferable visual models from natural language supervision")] is a vision–language model trained via contrastive learning on 400 million image–text pairs [[28](#bib.bib14 "Learning transferable visual models from natural language supervision"), [37](#bib.bib42 "Navigating data scarcity using foundation models: a benchmark of few-shot and zero-shot learning approaches in medical imaging")], to learn aligned multimodal embeddings. This objective enables CLIP to capture rich semantic and structural features that transfer effectively across diverse visual tasks [[15](#bib.bib7 "Are natural domain foundation models useful for medical image classification? in 2024 ieee/cvf winter conference on applications of computer vision (wacv). waikoloa, hi, usa: ieee;[cited 2024 aug 27]. 7619–7628")].
* •

  DINOv2 (DIstillation with NO labels) [[27](#bib.bib15 "Dinov2: learning robust visual features without supervision")] is a state-of-the-art self-supervised Vision Transformer trained on a curated dataset of 142M natural images using a self-distillation objective. It learns robust and transferable visual representations without manual annotations.
* •

  BiomedCLIP [[41](#bib.bib20 "Biomedclip: a multimodal biomedical foundation model pretrained from fifteen million scientific image-text pairs")] is a domain-specific extension of CLIP trained on PMC-15M, a large-scale biomedical dataset of 15M image–text pairs from PubMed Central. It captures fine-grained alignments between medical imagery and clinical context, enabling direct comparison between natural-domain and medical-domain pretrained representations.

### 3.1 Network Architecture

Our architecture follows an unrolled reconstruction paradigm, where a sequence of cascades iteratively refines the image. Each cascade consists of a data-consistency step in k-space and an image-domain refinement module. The data-consistency operation enforces agreement with acquired measurements, while the refinement module incorporates learned priors to improve reconstruction quality. In contrast to conventional approaches that rely on task-specific CNN priors, we introduce a foundation-model-guided denoiser, which leverages pretrained visual representations. This module integrates a frozen vision transformer encoder with a lightweight decoder, enabling the use of transferable features within each cascade. We first describe the architecture of the proposed foundation-model-based denoiser, followed by its integration within the unrolled reconstruction framework.

#### Foundation Model Denoiser.

Given an intermediate reconstruction, the complex-valued MRI image is converted to a magnitude image and normalized using percentile-based scaling [[7](#bib.bib34 "Do vision foundation models enhance domain generalization in medical image segmentation?")] to reduce outliers. The image is then replicated across three channels, resized to 224×224224\times 224, and standardized using ImageNet [[9](#bib.bib35 "Imagenet: a large-scale hierarchical image database")] statistics to match the input distribution of pretrained encoders. The normalized image is passed through a frozen Vision Transformer encoder (CLIP, DINOv2, or BiomedCLIP), whose parameters remain fixed throughout training to ensure that reconstruction is guided by pretrained representations rather than domain-specific adaptation. We refer to the resulting models as CMR-CLIP, CMR-DINOv2, and CMR-BiomedCLIP, respectively.

Instead of relying solely on the final transformer layer, we extract intermediate features from the first six layers, which capture low-level and structural information beneficial for reconstruction [[15](#bib.bib7 "Are natural domain foundation models useful for medical image classification? in 2024 ieee/cvf winter conference on applications of computer vision (wacv). waikoloa, hi, usa: ieee;[cited 2024 aug 27]. 7619–7628")]. These features are fused via a learnable mechanism: each layer is first aligned using LayerNorm [[2](#bib.bib36 "Layer normalization")], then combined using softmax-normalized weights constrained to sum to one [[16](#bib.bib26 "From clip to dino: visual encoders shout in multi-modal large language models")], enabling adaptive integration of multi-level representations. The fused patch tokens are reshaped into spatial feature maps and processed by a UNETR-style [[14](#bib.bib37 "Unetr: transformers for 3d medical image segmentation")] hierarchical decoder with multi-scale skip connections from intermediate encoder layers (layers 5, 4, and 3). Each skip feature is reshaped, resized via bilinear interpolation, and projected using 1×11\times 1 convolutions before fusion.

Each decoding stage consists of bilinear upsampling followed by convolutional refinement. In contrast to standard UNETR [[14](#bib.bib37 "Unetr: transformers for 3d medical image segmentation")] designs that employ full convolutions, we use depthwise separable convolutions (a 3×33\times 3 depthwise convolution followed by a 1×11\times 1 pointwise convolution) to improve parameter efficiency [[13](#bib.bib39 "Depthwise convolution is all you need for learning multiple visual domains")], along with instance normalization [[33](#bib.bib38 "Instance normalization: the missing ingredient for fast stylization")] and ReLU activation. At each stage, the upsampled features are concatenated with the corresponding multi-scale skip features from the encoder, as illustrated in Fig. [1](#S3.F1 "Figure 1 ‣ 3.2 Iterative Unrolled Reconstruction ‣ 3 Methodology ‣ Are Natural-Domain Foundation Models Effective for Accelerated Cardiac MRI Reconstruction?")(a), and further refined using a 3×33\times 3 convolution, instance normalization, and non-linearity. This process is repeated across multiple stages, progressively recovering spatial resolution and integrating both high-level and low-level information. To preserve fine-grained details, we additionally incorporate an input-level skip connection by projecting the original complex-valued reconstruction through a shallow convolutional layer and injecting it at the final decoding stage. The final output is produced via a lightweight convolutional head, yielding a two-channel reconstruction corresponding to the real and imaginary components. Overall, the proposed denoiser combines frozen foundation model features, multi-layer transformer fusion, and a lightweight hierarchical decoder to provide transferable yet task-adapted priors for MRI reconstruction.

### 3.2 Iterative Unrolled Reconstruction

Architectures based on unrolled optimization strategies have shown strong effectiveness in addressing inverse problems, particularly in accelerated MRI reconstruction [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction")]. These methods model reconstruction as a sequence of cascades, where each stage iteratively refines the estimate by enforcing data consistency and incorporating learned image priors.

Building on the E2E-VarNet framework [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], we adopt an unrolled reconstruction approach in the k-space domain, where the solution to the regularized inverse problem

|  |  |  |
| --- | --- | --- |
|  | x^=arg⁡minx⁡‖𝒜​(x)−k~‖22+ℛ​(x)\hat{x}=\arg\min\_{x}\;\left\|\mathcal{A}(x)-\tilde{k}\right\|\_{2}^{2}+\mathcal{R}(x) |  |

is approximated by unfolding the optimization into a sequence of TT cascades.
Each cascade corresponds to an update of the form:

|  |  |  |  |
| --- | --- | --- | --- |
|  | k^t+1=k^t−μt​M​(k^t−k~)+G​(k^t),\hat{k}^{t+1}=\hat{k}^{t}-\mu^{t}M(\hat{k}^{t}-\tilde{k})+G(\hat{k}^{t}), |  | (4) |

where k^t\hat{k}^{t} denotes the current estimate in k-space at cascade tt, μt\mu^{t} is a learnable step size, and G​(⋅)G(\cdot) represents a learned regularization term [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction")]. The second term enforces data consistency (DC) by ensuring that the reconstructed k-space remains aligned with the acquired measurements at sampled locations.

The regularization is applied in the image domain through our proposed foundation-model-guided denoiser. Specifically, the mapping G​(⋅)G(\cdot) can be expressed as:

|  |  |  |  |
| --- | --- | --- | --- |
|  | G​(k)=ℱ​(ℰ​(𝒟​(ℛ​(ℱ−1​(k))))),G(k)=\mathcal{F}\big(\mathcal{E}\big(\mathcal{D}\big(\mathcal{R}(\mathcal{F}^{-1}(k))\big)\big)\big), |  | (5) |

where 𝒟\mathcal{D} denotes the proposed denoiser, ℛ​(x1,…,xN)=∑i=1NSi∗​xi\mathcal{R}(x\_{1},\dots,x\_{N})=\sum\_{i=1}^{N}S\_{i}^{\*}x\_{i} is the reduction operator that combines multi-coil images using the corresponding sensitivity maps, and ℰ​(x)=(S1​x,…,SN​x)\mathcal{E}(x)=(S\_{1}x,\dots,S\_{N}x) is the expansion operator that maps the combined image back to individual coil images. This formulation enables the integration of learned image-domain priors within the iterative reconstruction process while maintaining consistency with the underlying acquisition model.
We estimate coil sensitivity maps using a standard sensitivity estimation module [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], where maps are derived from the low-frequency (ACS) region of the undersampled k-space data. These maps enable transformations between image space and multi-coil representations during reconstruction. Starting from the masked input k-space, the model applies a sequence of cascades, each performing data consistency in k-space followed by image-domain refinement using the proposed denoiser. After the final cascade, the reconstructed image is obtained via an inverse Fourier transform and combined across coils using root-sum-of-squares (RSS) [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")]. This iterative formulation allows the reconstruction to be progressively refined while jointly leveraging acquisition physics and transferable pretrained visual priors.

![Refer to caption](2604.22557v1/sec/denoiser_3.png)

(a) Proposed denoiser architecture. Multi-level features from the first six layers of the frozen vision encoder are fused using LayerNorm and learnable softmax weights. Selected intermediate layers (z5,z4,z3z\_{5},z\_{4},z\_{3}) provide spatially aligned skip connections, which are concatenated with decoder features at corresponding resolutions. A lightweight hierarchical decoder progressively upsamples and refines these features to generate the final reconstruction. Adapted from [[14](#bib.bib37 "Unetr: transformers for 3d medical image segmentation")]

![Refer to caption](2604.22557v1/sec/denoiser_unroll.png)

(b) Overview of the unrolled model architecture. Reconstruction is performed through TT cascades, each consisting of a data-consistency (DC) step in k-space and an image-domain refinement using the proposed denoiser. A sensitivity map estimator (SME) computes coil sensitivity maps, enabling transformations between image and multi-coil domains. Adapted from [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction")]

Figure 1: Overview of the proposed architecture.

## 4 Experiments

In this section, we present the experimental setup and evaluate the performance of the proposed method on both in-distribution and cross-domain reconstruction tasks. We first report results on the CMRxRecon [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")] dataset, where models are trained and tested on cardiac MRI data under varying acceleration factors (×4\times 4, ×8\times 8, and ×10\times 10). Reconstruction quality is assessed using standard metrics, including SSIM, PSNR, and NMSE. In particular, we emphasize the structural similarity index measure (SSIM) [[35](#bib.bib40 "Multiscale structural similarity for image quality assessment")], which is widely regarded as the primary evaluation metric in medical image reconstruction [[12](#bib.bib5 "Humus-net: hybrid unrolled multi-scale network architecture for accelerated mri reconstruction")].

To further evaluate generalization, we consider challenging cross-domain settings by training models on CMRxRecon [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")] and testing them on anatomically distinct datasets from fastMRI [[40](#bib.bib29 "FastMRI: an open dataset and benchmarks for accelerated mri")], including knee and brain MRI. This setup enables us to assess the robustness of the proposed approach under significant domain shifts.

### 4.1 CMRxRecon Dataset

The CMRxRecon dataset [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")] consists of 120 cardiac MRI cases acquired on 3T scanners, providing fully sampled dynamic cine and multi-contrast raw k-space data. The cine sequences include multiple standard cardiac views, such as short-axis (SAX) and long-axis views (2-chamber, 3-chamber, and 4-chamber), while the multi-contrast acquisitions comprise T1-weighted and T2-weighted images. For our experiments, we use the provided fully sampled data to simulate undersampling with acceleration factors of ×4\times 4, ×8\times 8, and ×10\times 10 using uniform sampling patterns, along with corresponding masks and 24 auto-calibration (ACS) lines [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")]. The dataset is split into training, validation, and test sets using a 70%/10%/20% partition, resulting in 17,916 training samples, 2,664 validation samples, and 5,112 test samples. All models are trained and evaluated on this split for in-distribution experiments.

### 4.2 fastMRI Dataset

To evaluate cross-domain generalization, we test models trained on CMRxRecon [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")] on the fastMRI dataset [[40](#bib.bib29 "FastMRI: an open dataset and benchmarks for accelerated mri"), [32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], which consists of fully sampled knee and brain MRI scans acquired on 1.5T and 3T scanners. The knee subset includes coronal proton density-weighted images with and without fat suppression, while the brain subset contains axial T1-weighted, T2-weighted, and FLAIR sequences. For evaluation, we use a subset of 1,767 knee images and 3,168 brain images. Undersampling is simulated using equispaced sampling masks with center fractions of 0.04 and 0.08 [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], corresponding to different amounts of low-frequency information. We consider acceleration factors of ×4\times 4, ×8\times 8, and ×10\times 10 to assess performance under varying reconstruction difficulty in cross-domain settings.

### 4.3 Implementation Details

Our framework is implemented following the standard unrolled reconstruction setting. All input images are resized to 224×224224\times 224 to match the input requirements of the pretrained vision encoders. We compare our method against the state-of-the-art E2E-VarNet [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], which we reimplement using the same architecture and hyperparameters for a fair comparison. To ensure consistency, we adopt the same sensitivity map estimation network as E2E-VarNet across all models. All reconstruction models are trained with 1212 cascades (unrolled iterations). The baseline E2E-VarNet contains approximately 29.929.9M trainable parameters, while our foundation-model-based approach has approximately 5656M trainable parameters due to the additional decoder and fusion components, with the foundation model encoder kept frozen. We train separate models for acceleration factors of ×4\times 4, ×8\times 8, and ×10\times 10. The models are optimized using the Adam optimizer with an initial learning rate of 1×10−31\times 10^{-3}, which is decayed by a factor of 0.10.1 after 4040 epochs. We use no weight decay. Training is performed for 5050 epochs with early stopping based on validation performance (patience of 55 epochs). We minimize the SSIM loss [[35](#bib.bib40 "Multiscale structural similarity for image quality assessment"), [32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")] between the reconstructed and target images. For the sensitivity estimation network, we use 44 pooling layers and 88 base channels, consistent with prior work [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")]. All experiments were conducted on NVIDIA RTX 4090 and RTX 3090 GPUs.

## 5 Results

### 5.1 In-Distribution Reconstruction Results

We first evaluate the proposed method on the CMRxRecon dataset [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")], where models are trained and tested on cardiac MRI data under varying acceleration factors.

Table [1](#S5.T1 "Table 1 ‣ 5.1 In-Distribution Reconstruction Results ‣ 5 Results ‣ Are Natural-Domain Foundation Models Effective for Accelerated Cardiac MRI Reconstruction?") summarizes reconstruction performance on the CMRxRecon test set across acceleration factors of ×4\times 4, ×8\times 8, and ×10\times 10. Qualitative comparisons are shown in Fig. [2](#S5.F2 "Figure 2 ‣ 5.1 In-Distribution Reconstruction Results ‣ 5 Results ‣ Are Natural-Domain Foundation Models Effective for Accelerated Cardiac MRI Reconstruction?"). As expected, the task-specific E2E-VarNet [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")] consistently achieves the best results across all metrics, benefiting from end-to-end supervision tailored to MRI reconstruction.

Foundation-model-based approaches, while using frozen encoders pretrained on natural or biomedical data, remain competitive. At ×4\times 4, CLIP achieves an SSIM of 0.95850.9585 compared to 0.96760.9676 for E2E-VarNet, and similar trends persist at ×8\times 8 and ×10\times 10, with the performance gap widening as acceleration increases. This reflects the growing difficulty of the reconstruction problem, where task-specific model retain an advantage in in-distribution settings.

Among foundation models, performance differences are relatively small. CMR-CLIP performs best at lower acceleration factors (×4\times 4 and ×8\times 8), indicating that natural-image pretraining provides strong general-purpose representations. At higher acceleration (×10\times 10), CMR-BiomedCLIP becomes the strongest variant, achieving the highest SSIM (0.92400.9240), suggesting that domain-specific pretraining offers advantages in more ill-posed regimes.

Overall, while task-specific architecture remain superior in standard settings, foundation models achieve competitive performance without MRI-specific training, demonstrating their ability to learn transferable structural priors.

Table 1: Reconstruction performance on the CMRxRecon test set under different acceleration factors. Best results in bold, second-best underlined.

| Acc. | Method | SSIM ↑\uparrow | PSNR ↑\uparrow | NMSE ↓\downarrow |
| --- | --- | --- | --- | --- |
| ×4\times 4 | E2E-VarNet | 0.9676 | 41.29 | 0.0154 |
| CMR-CLIP | 0.9585 | 40.12 | 0.0226 |
| CMR-DINOv2 | 0.9548 | 39.57 | 0.0249 |
| CMR-BiomedCLIP | 0.9557 | 39.67 | 0.0252 |
| ×8\times 8 | E2E-VarNet | 0.9502 | 38.21 | 0.0227 |
| CMR-CLIP | 0.9359 | 36.83 | 0.0340 |
| CMR-DINOv2 | 0.9340 | 36.65 | 0.0340 |
| CMR-BiomedCLIP | 0.9358 | 36.79 | 0.0343 |
| ×10\times 10 | E2E-VarNet | 0.9417 | 37.32 | 0.0262 |
| CMR-CLIP | 0.9215 | 35.51 | 0.0418 |
| CMR-DINOv2 | 0.9223 | 35.54 | 0.0419 |
| CMR-BiomedCLIP | 0.9240 | 35.73 | 0.0401 |

![Refer to caption](2604.22557v1/In_domain_acc_8.png)

Figure 2: Qualitative results at ×8\times 8 acceleration. From top to bottom: E2E-VarNet, CMR-CLIP, CMR-DINOv2, and CMR-BiomedCLIP. Columns show the target image, reconstruction, error map, and zero-filled input, respectively.

![Refer to caption](2604.22557v1/sec/ood_results_2.png)

Figure 3: Out-of-distribution qualitative results. Visual comparison on fastMRI knee (left) and brain (right) datasets at ×10\times 10 acceleration and center fraction 0.08. From top to bottom: E2E-VarNet, CMR-CLIP, and CMR-BiomedCLIP. Columns show the target image, reconstruction, error map, and zero-filled input, respectively. Red boxes highlight regions with notable differences in structural fidelity.

### 5.2 Cross-Domain Generalization Results

We evaluate the generalization capability of the proposed approach under challenging cross-domain settings by training on the CMRxRecon dataset [[34](#bib.bib28 "CMRxRecon: an open cardiac mri dataset for the competition of accelerated image reconstruction")] and testing on the fastMRI knee and brain datasets [[40](#bib.bib29 "FastMRI: an open dataset and benchmarks for accelerated mri")]. These datasets differ substantially in anatomical structure, image contrast, and acquisition characteristics, making this a stringent test of robustness. In addition to the domain shift in anatomy, we introduce a further mismatch in the sampling patterns. During training, models are exposed to equispaced undersampling masks with fixed auto-calibration signal (ACS) lines (24 central k-space lines). At test time, however, we use equispaced masks defined by center fractions of 0.04 and 0.08 [[32](#bib.bib27 "End-to-end variational networks for accelerated mri reconstruction")], where the center fraction specifies the proportion of low-frequency k-space that is fully sampled. This results in a different distribution of sampling patterns and reduces the amount of low-frequency information available, making reconstruction significantly more challenging.
Together, these shifts in anatomy, contrast, and sampling strategy create a realistic and demanding evaluation setting for assessing the robustness and transferability of learned reconstruction priors.
Quantitative results are reported in Tables [2](#S5.T2 "Table 2 ‣ Analysis and Discussion. ‣ 5.2 Cross-Domain Generalization Results ‣ 5 Results ‣ Are Natural-Domain Foundation Models Effective for Accelerated Cardiac MRI Reconstruction?") and [3](#S5.T3 "Table 3 ‣ Analysis and Discussion. ‣ 5.2 Cross-Domain Generalization Results ‣ 5 Results ‣ Are Natural-Domain Foundation Models Effective for Accelerated Cardiac MRI Reconstruction?"), with corresponding qualitative comparisons shown in Fig. [3](#S5.F3 "Figure 3 ‣ 5.1 In-Distribution Reconstruction Results ‣ 5 Results ‣ Are Natural-Domain Foundation Models Effective for Accelerated Cardiac MRI Reconstruction?").

#### Analysis and Discussion.

The cross-domain results on fastMRI knee and brain datasets reveal several important trends regarding the behavior of foundation-model-based priors under distribution shift.
At lower acceleration (×4\times 4), E2E-VarNet consistently achieves the best performance across both knee and brain datasets. This is expected, as fully supervised reconstruction models are optimized for the training distribution and can effectively exploit dataset-specific priors when sufficient measurements are available. However, as reconstruction becomes more challenging, through higher acceleration (×8\times 8, ×10\times 10) and reduced center fraction (0.04), a clear shift in behavior emerges. The performance of E2E-VarNet degrades more rapidly, while foundation-model-based approaches exhibit more stable performance and consistently match or outperform E2E-VarNet.

This trend is consistent across both anatomical domains. On the knee dataset, CMR-BiomedCLIP achieves the best performance at ×8\times 8, while CMR-CLIP and CMR-BiomedCLIP outperform E2E-VarNet at ×10\times 10, particularly under reduced center fraction. Similarly, on the brain dataset, foundation models surpass E2E-VarNet at ×8\times 8 and ×10\times 10, with CMR-BiomedCLIP achieving the strongest overall performance at the highest acceleration. These gains are most pronounced under center fraction 0.04, where limited low-frequency information increases reconstruction ambiguity and places greater reliance on learned priors.

Comparing foundation models, CMR-CLIP performs strongly at moderate acceleration, indicating that natural-image pretraining captures highly transferable structural representations. CMR-BiomedCLIP provides additional gains in more ill-posed regimes, suggesting that domain-specific pretraining becomes beneficial as reconstruction difficulty increases. In contrast, CMR-DINOv2 consistently underperforms across settings, particularly under severe domain shift, likely due to the absence of cross-modal alignment in its pretraining objective [[19](#bib.bib41 "Data or language supervision: what makes clip better than dino?")], which may limit its ability to encode higher-level structural priors necessary for robust MRI reconstruction.

Overall, these results suggest a regime-dependent behavior: task-specific model excel in in-distribution and well-conditioned settings, while pretrained foundation models provide more robust and transferable priors under severe undersampling and domain shift. This highlights the potential of leveraging large-scale pretrained representations as a complementary alternative to conventional task-specific reconstruction pipelines, particularly in scenarios where training data is mismatched.

Table 2: OOD reconstruction performance on the FastMRI Knee dataset under different acceleration factors. Best results in bold, second-best underlined.

| Acc | Method | Center frac = 0.08 | | | Center frac = 0.04 | | |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | SSIM ↑\uparrow | PSNR ↑\uparrow | NMSE ↓\downarrow | SSIM ↑\uparrow | PSNR ↑\uparrow | NMSE ↓\downarrow |
| 4x | E2E-VarNet | 0.8061 | 31.06 | 0.0280 | 0.7769 | 29.21 | 0.0412 |
| CMR-CLIP | 0.7864 | 30.88 | 0.0288 | 0.7387 | 27.92 | 0.0548 |
| CMR-DINOv2 | 0.7412 | 27.50 | 0.0647 | 0.6873 | 21.91 | 0.2781 |
| CMR-BiomedCLIP | 0.7848 | 30.66 | 0.0302 | 0.7310 | 27.60 | 0.0591 |
| 8x | E2E-VarNet | 0.7161 | 28.59 | 0.0479 | 0.6552 | 25.88 | 0.0876 |
| CMR-CLIP | 0.7232 | 28.72 | 0.0470 | 0.6668 | 26.17 | 0.0820 |
| CMR-DINOv2 | 0.7137 | 27.33 | 0.0646 | 0.6566 | 25.61 | 0.0932 |
| CMR-BiomedCLIP | 0.7285 | 28.84 | 0.0457 | 0.6712 | 26.26 | 0.0804 |
| 10x | E2E-VarNet | 0.6956 | 28.08 | 0.0542 | 0.6287 | 25.26 | 0.1014 |
| CMR-CLIP | 0.7150 | 28.36 | 0.0509 | 0.6576 | 26.08 | 0.0839 |
| CMR-DINOv2 | 0.6960 | 27.03 | 0.0684 | 0.6244 | 24.73 | 0.1148 |
| CMR-BiomedCLIP | 0.7133 | 28.55 | 0.0491 | 0.6545 | 25.91 | 0.0873 |

Table 3: OOD reconstruction performance on the FastMRI Brain dataset under different acceleration factors. Best results in bold, second-best underlined.

| Acc | Method | Center frac = 0.08 | | | Center frac = 0.04 | | |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  | SSIM ↑\uparrow | PSNR ↑\uparrow | NMSE ↓\downarrow | SSIM ↑\uparrow | PSNR ↑\uparrow | NMSE ↓\downarrow |
| 4x | E2E-VarNet | 0.8209 | 30.29 | 0.0241 | 0.7670 | 27.23 | 0.0483 |
| CMR-CLIP | 0.7962 | 29.69 | 0.0281 | 0.7208 | 25.79 | 0.0682 |
| CMR-DINOv2 | 0.7321 | 25.65 | 0.0808 | 0.6531 | 20.59 | 0.3796 |
| CMR-BiomedCLIP | 0.7985 | 29.52 | 0.0290 | 0.7163 | 25.43 | 0.0747 |
| 8x | E2E-VarNet | 0.7363 | 27.25 | 0.0473 | 0.6416 | 23.74 | 0.1069 |
| CMR-CLIP | 0.7391 | 27.36 | 0.0462 | 0.6505 | 23.99 | 0.1006 |
| CMR-DINOv2 | 0.7203 | 25.28 | 0.0753 | 0.6300 | 22.86 | 0.1309 |
| CMR-BiomedCLIP | 0.7447 | 27.14 | 0.0483 | 0.6514 | 23.88 | 0.1035 |
| 10x | E2E-VarNet | 0.7234 | 26.84 | 0.0520 | 0.6209 | 23.33 | 0.1172 |
| CMR-CLIP | 0.7261 | 26.22 | 0.0594 | 0.6312 | 23.32 | 0.1166 |
| CMR-DINOv2 | 0.7142 | 25.42 | 0.0730 | 0.6135 | 22.63 | 0.1407 |
| CMR-BiomedCLIP | 0.7326 | 26.87 | 0.0515 | 0.6374 | 23.47 | 0.1134 |

## 6 Conclusion

We present the first study investigating frozen vision foundation models as priors for physics-based MRI reconstruction, introducing an unrolled framework that integrates pretrained visual encoders within each cascade. While task-specific models such as E2E-VarNet achieve superior performance in standard in-distribution settings, foundation-model-based approaches demonstrate greater robustness under cross-domain shifts and severe undersampling, where the reconstruction problem becomes increasingly ill-posed. Notably, as reconstruction difficulty increases, these models provide more stable and transferable priors, narrowing and in some cases surpassing the performance gap with the supervised baseline. Furthermore, we find that natural-image-pretrained models such as CLIP already capture highly transferable structural representations, with domain-specific pretraining BiomedCLIP offering modest additional gains in challenging regimes. Overall, our findings highlight the potential of large-scale pretrained visual representations as a complementary source of priors for improving robustness and generalization in MRI reconstruction and, more broadly, in physics-based inverse problems.

## Acknowledgements

This work was supported by Taighde Éireann–Research Ireland under Grant numbers 18/CRT/6183 & 12/RC/2289 P2.


# 歸檔時間: 2026-04-27 19:20:18
### 文獻名稱
Holo360D: A Large-Scale Real-World Dataset with Continuous Trajectories for Advancing Panoramic 3D Reconstruction and Beyond

### 文獻中文名稱
全景 3D 重建的突破：Holo360D 大規模真實世界資料集，提供連續視角軌跡與精準深度地圖

- 論文來源 URL: https://arxiv.org/abs/2604.22482
- 抓取時間: 2026-04-27 11:08 UTC

### 一句話核心
研究者用專業 3D 掃描設備拍攝超過 11 萬張全景照片，打造全景 3D 重建的新標準資料集。

### 30 秒看懂這篇論文
- 解決什麼問題：現有全景 3D 重建模型在處理球形扭曲的全景照片時表現不佳，且資料量不足。
- 方法是什麼：像拍照集錦一樣，用手持掃描器連續走動拍攝，並用離線重建補完細節。
- 結果如何：資料集含 11 萬張全景照，視角間距僅 0.29 公尺，深度圖完整度達 0.86。

### 先備知識
- 全景影像：像是 360 度相機拍攝的照片，可以環視四周。
- 深度圖：表示物體距離相機遠近的照片，越靠近物體越亮。
- 視差：同一物體在不同視角下看起來位置會移動，可以用來重建 3D 形狀。

### 重要名詞
1. **全景影像**：它重要是因為可以 360 度環視；它改善了只能拍直觀角度的限制。
2. **深度圖**：它重要是提供物體遠近資訊；它讓 3D 重建不需要測量儀器。
3. **視差匹配**：它重要是用多視角重建 3D；它解決單圖深度預測不準確的問題。

### 研究動機
- 背景：AI 模型可以從照片重建 3D 世界，但大多只能處理單點視角的照片，對全景影像表現差。
- 痛點：現有的全景資料集規模小，深度圖不完整，且視角間隔太大，不利於訓練。
- 目標：提供大規模、高品質、視角連續的全景資料集，讓 3D 重建模型學會處理全景影像。

### 方法流程
1. **資料收集**：用結合雷射掃描與 360 度相機的手持設備，像逛展覽一樣連續拍攝。
2. **離線重建**：把原始資料拿去進行_bundle adjustment_，像是用拼圖軟體把照片與 3D 點雲對齊。
3. **網格重建**：用_Poisson 重建_的方法，把點雲轉成網格模型，就像用 3D 列印做出物體表面。
4. **後處理淨化**：移除異常點、填補玻璃區域的缺口，像是清理 3D 模型的雜質。
5. **區域性重網格化**：針對複雜細節（如金屬柵欄），用高分辨率重現細節。
6. **深度圖生成**：從網格與點雲投影出對應的深度圖。

### 圖表導讀
- 圖表重點：圖 1 顯示 Holo360D 的深度圖比 Stanford2D3D、Matterport3D、Depth360 等資料集完整度高出許多。
- 怎麼看：室內完整度 0.86、室外 0.82，遠勝其他資料集。
- 新手重點：深度圖越完整，AI 重建的 3D 模型就越精準。

### 驚人發現與具體數據
1. **連續視角優勢**：Holo360D 的視角間距僅 0.29 公尺，遠優於 KITTI-360 (1.01 公尺) 和 360Loc (0.49 公尺)。
2. **深度完整性**：室內深度圖完整度 0.86、室外 0.82，比 Stanford2D3D (0.72) 和 360Loc (0.62) 都高。
3. **對齊精準度**：全景與深度圖的平均對齊誤差僅 5.03 像素，優於其他資料集。

### 這對我有什麼意義？
- 應用 1：用手機 360 度相機就能重建房間 3D 模型，用於 VR 看房。
- 應用 2：AR 擴增實境遊戲可以精準貼合真實場景，物體不會穿牆。
- 應用 3：建築設計可以用全景掃描快速建立室內模型，節省傳統測量時間。

### 理解檢查
Q: 這篇論文最主要想解決什麼問題？
A. 用手機拍攝高品質 360 度照片
B. 提供大規模、高品質、視角連續的全景 3D 重建資料集
C. 開發新的全景相機硬體設備
D. 用 AI 生成逼真的 3D 建築模型
答案: B
解釋: 論文核心是用專業設備收集資料，解決現有全景資料集規模小、深度不完整、視角斷裂的問題。

### 延伸閱讀
1. **VGGT**：視覺幾何 grounded 變分架構，可同時預測物體深度、點雲與相機姿態。
2. **π³ (pi-cube)**：無參考框架的 3D 視覺模型，在 Holo360D 上表現更好。
3. **DUST3R**：先鋒性的幾何 3D 視覺模型，為後續許多 3D 重建研究打下基礎。
