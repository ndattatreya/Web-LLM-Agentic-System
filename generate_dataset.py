import json
import random

# Paste the above 60 samples into a list called base_data

base_data = [
  {"text": "Artificial intelligence is transforming industries through automation.", "label": 1},
  {"text": "Machine learning models improve accuracy with more data.", "label": 1},
  {"text": "Cloud computing enables scalable storage and computing resources.", "label": 1},
  {"text": "Cybersecurity protects systems from unauthorized access.", "label": 1},
  {"text": "Blockchain ensures secure and transparent transactions.", "label": 1},

  {"text": "Water boils at 100 degrees Celsius under normal conditions.", "label": 1},
  {"text": "Gravity pulls objects toward the Earth.", "label": 1},
  {"text": "The human brain processes information through neurons.", "label": 1},
  {"text": "The heart pumps blood throughout the body.", "label": 1},
  {"text": "Photosynthesis converts sunlight into energy.", "label": 1},

  {"text": "The Indian independence movement led to freedom in 1947.", "label": 1},
  {"text": "The stock market reflects economic conditions.", "label": 1},
  {"text": "Electric vehicles reduce carbon emissions.", "label": 1},
  {"text": "Renewable energy sources are environmentally friendly.", "label": 1},
  {"text": "Education plays a key role in societal development.", "label": 1},

  {"text": "Regular exercise improves physical and mental health.", "label": 1},
  {"text": "A balanced diet is essential for well-being.", "label": 1},
  {"text": "Reading books enhances knowledge and creativity.", "label": 1},
  {"text": "Time management increases productivity.", "label": 1},
  {"text": "Communication skills are important in professional life.", "label": 1},

  {"text": "Chapter 1 Introduction", "label": 0},
  {"text": "Table of contents", "label": 0},
  {"text": "Figure 2 shows the architecture", "label": 0},
  {"text": "Step 1: Click the button", "label": 0},
  {"text": "Refer to the diagram below", "label": 0},

  {"text": "Section 3.2 Overview", "label": 0},
  {"text": "Page 5 of 10", "label": 0},
  {"text": "Appendix A details", "label": 0},
  {"text": "See the table above", "label": 0},
  {"text": "Algorithm 1 description", "label": 0},

  {"text": "Contact us Privacy policy Terms of service", "label": 0},
  {"text": "Login Sign up Forgot password", "label": 0},
  {"text": "Click here to apply now", "label": 0},
  {"text": "Read more Next page Previous", "label": 0},
  {"text": "Subscribe to our newsletter", "label": 0},

  {"text": "© 2024 All rights reserved", "label": 0},
  {"text": "Home About Services Careers Contact", "label": 0},
  {"text": "Add to cart Buy now", "label": 0},
  {"text": "Share Like Comment Subscribe", "label": 0},
  {"text": "Download now Free trial available", "label": 0},

  {"text": "Back to top", "label": 0},
  {"text": "Loading please wait", "label": 0},
  {"text": "Click here for more details", "label": 0},
  {"text": "Submit your response", "label": 0},
  {"text": "View all results", "label": 0},

  {"text": "This article explains machine learning concepts in detail.", "label": 1},
  {"text": "The ecosystem depends on balanced environmental conditions.", "label": 1},
  {"text": "Economic growth depends on multiple factors.", "label": 1},
  {"text": "Healthcare systems are essential for public well-being.", "label": 1},
  {"text": "Technology continues to evolve rapidly.", "label": 1},

  {"text": "Figure 3 illustrates the workflow process.", "label": 0},
  {"text": "Step 2: Enter your details", "label": 0},
  {"text": "Click next to continue", "label": 0},
  {"text": "Download the file here", "label": 0},
  {"text": "Proceed to checkout", "label": 0}
] # paste sample here

dataset = []

for _ in range(1000):
    item = random.choice(base_data)
    dataset.append(item)

random.shuffle(dataset)

with open("dataset_final_1000.json", "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print("✅ dataset_final_1000.json ready")