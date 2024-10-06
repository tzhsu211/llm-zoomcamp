# Project Overview

There are numerous nutritional supplements available on the market, and many people often struggle with how to choose the right ones for their specific needs. This app allows users to ask questions related to nutritional supplements, and the model recommends products tailored to their individual requirements. Additionally, users can provide feedback on the model's recommendations, enabling the backend to assess and improve its performance.

This is a project for [LLM Zoomcamp](https://github.com/DataTalksClub/llm-zoomcamp).

## Workflow

When the project is running, the user experience will follow these steps:

1. **User Input**: The user enters their question regarding nutritional supplements.
2. **Vegan Option**: The user checks a box to indicate whether they are a vegan
3. **Model Selection**: The user selects the desired model for generating responses.
4. **API Input**: If necessary, the user inputs their API key.
5. **Submit Query**: Finally, the user submits their question to receive tailored recommendations.
6. **Feedback**: Based on the model's response, users can provide feedback by giving a thumbs up or thumbs down on the answer.

## Dataset
I asked ChatGPT to generate information for common nutritional supplements. Ultimately, data for 53 different types of supplements was generated. The structure of the data includes:
* name: The name of the nutritional supplement.
* purpose: The primary purpose of the nutritional supplement, explaining its benefi ts.
* who_should_not_use: A description of individuals who should avoid the supplement due to potential health risks.
* common_side_effects: A list of common side effects associated with the supplement.
* recommended_dosage: The suggested daily dosage for optimal benefits.
* source: Information about the origin of the supplement (e.g., synthetic, natural).
* vegan_friendly: A boolean value indicating whether the supplement is suitable for vegans.

Below is an example of the dataset in JSON format:
``` json
{
    "name": "Vitamin C",
    "purpose": "Immune support and antioxidant",
    "who_should_not_use": "People with kidney stones",
    "common_side_effects": "Gastrointestinal upset, headache",
    "recommended_dosage": "500-1000 mg daily",
    "source": "Synthetic",
    "vegan_friendly": true
}

```

## 
