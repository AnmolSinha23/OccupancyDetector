# How We Built an Explainable Room Occupancy Detector Using Sensor Data
### A Plain-Language Engineering Report by Two 2nd-Year B.Tech Students
**Project:** Room Occupancy Detection from Environmental Sensor Streams  
**Core Technologies:** Python, Pandas, Scikit-Learn, Matplotlib, Streamlit  
**Dataset Source:** UCI Machine Learning Repository (Dataset ID: 357)  
**Foundational Research Paper:** Candanedo & Feldheim, *Energy and Buildings* (2016)

---

## 1. What is this project in plain English? (The 30-Second Elevator Pitch)

Imagine walking into an office room. You do not install any cameras, you do not put up microphones, and you do not ask people to swipe badges. Instead, you put a small sensor box on the desk that measures four simple physical quantities:
1. **Light** (how bright is the room, in Lux?)
2. **$\text{CO}_2$ concentration** (how much carbon dioxide is in the air, in parts per million?)
3. **Temperature** (in degrees Celsius)
4. **Relative Humidity** (in percent)

Our project takes these numbers and predicts with **over 97% to 99% accuracy** whether the room is **Occupied (someone is inside)** or **Empty (nobody is inside)**. 

Even better: our best model is not a mysterious deep neural network or an unexplainable "black box." It is a tiny, clean **Decision Tree of depth 3** that works like a simple flowchart of 3 questions. Anyone—a professor, a lab examiner, or an electrician installing an air conditioner—can look at the rules on paper and verify why the model made a prediction.

---

## 2. Why did we make this? (The Real-World Problem)

### The Problem of "Dumb" Buildings
Commercial buildings, college campuses, and office complexes waste an enormous amount of electricity:
- Air conditioners and central heating blast all day long in empty conference halls and classrooms.
- Tube lights stay turned on across vacant corridors and cabins for hours.
- Building management systems usually run on **rigid, dumb timers** (e.g., "keep AC on from 8:00 AM to 6:00 PM"). If people leave early or a meeting gets cancelled, energy is burned for nothing.

### Why not just use cameras or microphones?
When people first think of occupancy detection, their immediate reaction is: *"Why not put a webcam or an overhead camera with YOLO/OpenCV?"*
As two computer science students, we realized very quickly why companies and universities hate that solution:
1. **Privacy & Creepiness:** Nobody wants a camera staring at their desk all day. In many countries (and under GDPR regulations), putting cameras in private cabins is outright illegal or heavily restricted.
2. **Compute & Hardware Cost:** Running video feeds requires expensive cameras, high network bandwidth, and power-hungry GPUs.
3. **Audio is just as bad:** Putting microphones in a room captures private phone calls and confidential conversations.

### Why not ordinary PIR (motion) sensors?
Most existing automatic lights use Passive Infrared (PIR) motion sensors. But everyone who has studied in a modern library knows their fatal flaw: **the "statue problem."**  
If you sit quietly reading a textbook or typing on your laptop without waving your arms around, a PIR sensor assumes the room is empty and suddenly turns the lights off on you!

### The Sweet Spot: Environmental Ambient Telemetry
Humans are warm-blooded mammals that breathe and need light to work. When a human sits in an office:
- They turn on the lights ($\text{Light}$ jumps from 0 to 400+ Lux).
- They exhale carbon dioxide ($\text{CO}_2$ concentration steadily climbs from outdoor ambient ~400 ppm to 800–1200+ ppm).
- Their body emits heat (~100 Watts per person) and water vapor.

These sensors are **cheap**, **low-power**, **100% privacy-friendly**, and they detect presence **even when you sit completely motionless**.

---

## 3. What paper does our project build upon?

Our project is rooted in the research paper:
> **Candanedo, L. M., & Feldheim, V. (2016).**  
> *"Accurate occupancy detection of an office room from light, temperature, humidity and CO2 measurements using statistical learning models."*  
> Published in *Energy and Buildings*, Volume 112, pages 28–39.

### What the original authors did:
- In February 2015, the authors instrumented a single office room ($3.1\text{ m} \times 5.8\text{ m} \times 2.7\text{ m}$) at the University of Mons in Belgium with digital sensors logging data every minute.
- Ground truth occupancy (0 or 1) was recorded using time-stamped pictures taken every minute by an automated camera setup (the camera was only used to label the data during research, not during live prediction).
- They trained five classical statistical models in R: Linear Discriminant Analysis (LDA), Classification and Regression Trees (CART), Random Forest (RF), Gradient Boosting (GBM), and Support Vector Machines (SVM).
- They made their raw dataset publicly available on the UCI Machine Learning Repository (UCI ID 357).

### What was left missing or unanswered?
While their paper proved that statistical models could work, it left several practical engineering questions untouched:
1. **Sensor Cost & Redundancy:** An NDIR $\text{CO}_2$ sensor costs \$15–\$30, while a photodiode light sensor costs \$0.50. Can we drop sensors to make the hardware cheaper without losing accuracy?
2. **Static Snapshots vs. Dynamic Rates:** The paper looked at static instantaneous readings. But human occupancy is fundamentally dynamic—$\text{CO}_2$ rises when you enter and falls when you leave. Can simple past-only trend features help?
3. **The Door-Open Problem:** When the office door was left open, $\text{CO}_2$ diffused into the corridor, causing static models to struggle. How can we fix this?
4. **Explainability & Usability:** The original research was written in complex R scripts with academic charts. There was no interactive interface or plain-language model a student or engineer could test in real time.

This is exactly where our project steps in.

---

## 4. What is NEW in our work? (Our Contributions as a Team)

We did not just download someone else's dataset and blindly call `.fit()` and `.predict()`. We added four major original contributions:

```
+---------------------------------------------------------------------------------------+
|                               OUR TEAM'S CONTRIBUTIONS                                |
+---------------------------------------------------------------------------------------+
| 1. SENSOR ABLATION STUDY       -> Tested leave-one-out and single-sensor models.     |
|                                   Found that Humidity is 100% redundant and can be    |
|                                   dropped to reduce IoT hardware costs.               |
|                                                                                       |
| 2. CAUSAL TREND FEATURES       -> Engineered 5-minute past-only rate-of-change        |
|                                   (CO2 slope) & Light rolling average. Boosted open-  |
|                                   door Decision Tree accuracy from 97.67% to 99.27%!  |
|                                                                                       |
| 3. LEAK-FREE VALIDATION        -> Proved why random K-Fold cross validation is        |
|                                   invalid for time-series sensor data and used strict |
|                                   chronological splitting.                            |
|                                                                                       |
| 4. INTERACTIVE WEB APP         -> Built a clean Streamlit interface with physics-     |
|                                   accurate HumidityRatio calculation and instant      |
|                                   confidence probabilities.                           |
+---------------------------------------------------------------------------------------+
```

---

## 5. The Dataset: What's inside and what did we find?

When we wrote our data loading script (`src/data_loading.py`), we did not make any assumptions. We wrote Python code to download the official zip file directly from the UCI archive, extract it, and inspect the raw text lines.

### The Three Files
The dataset is split into three distinct time periods:
1. **`datatraining.txt` (Training Set):** 8,143 rows recorded from Feb 4 to Feb 10, 2015. The office door was kept closed during working hours.
2. **`datatest.txt` (Test Set 1 - Door Closed):** 2,665 rows recorded from Feb 2 to Feb 4, 2015. The door was closed, just like training.
3. **`datatest2.txt` (Test Set 2 - Door Open):** 9,752 rows recorded from Feb 11 to Feb 18, 2015. The door was left mostly open.

Notice an interesting detail: **Test Set 1 was recorded BEFORE the training set, and Test Set 2 was recorded AFTER the training set!** This gave us a true real-world test: our model must generalize backwards in time (Test 1) and forwards into a changed environment (Test 2).

### Summary Statistics We Measured

| Dataset | Total Rows | Date Range | Empty (0) Rows | Occupied (1) Rows | Class Balance | Missing Values |
|---|---|---|---|---|---|---|
| **Training** | 8,143 | Feb 4 – Feb 10, 2015 | 6,414 | 1,729 | 78.8% Empty / 21.2% Occupied | **0** |
| **Test 1 (Door Closed)** | 2,665 | Feb 2 – Feb 4, 2015 | 1,693 | 972 | 63.5% Empty / 36.5% Occupied | **0** |
| **Test 2 (Door Open)** | 9,752 | Feb 11 – Feb 18, 2015 | 7,703 | 2,049 | 79.0% Empty / 21.0% Occupied | **0** |

### A Hidden Quirk in the Raw Files
When we opened the raw files in Python, we noticed something funny:
- The header line had **7 column names**: `"date","Temperature","Humidity","Light","CO2","HumidityRatio","Occupancy"`.
- But every data row had **8 values**: `"1","2015-02-04 17:51:00",23.18,27.272,426,721.25,0.00479,1`.

The very first number (`"1"`) was an unnamed row index generated by R's `write.table()`! If you blindly parse this without checking, your columns will shift by one and your model will try to predict occupancy using dates or timestamps. By inspecting the file first, we handled it cleanly by letting `pandas` use that first column as the index.

### Checking the Sampling Clock
Before creating any historical features, we wrote a small script to measure the time gap between consecutive rows:
```
Difference mode: 0 days 00:01:00 (exactly 60 seconds)
```
This was a key finding: **every single row represents exactly 1 minute of real time**. This meant we didn't have to guess: a 5-minute time window is strictly 5 rows in pandas (`.shift(5)`).

---

## 6. How does our system work under the hood? (The Techniques in Plain Terms)

We deliberately chose simple, standard algorithms that we can explain line by line:

### Technique 1: Decision Tree (Our Star Model)
Think of a Decision Tree as playing a game of **"20 Questions"** with the sensors:
- *"Is Light greater than 365 Lux?"* If no, the room is almost certainly dark and empty.
- If yes, *"Is $\text{CO}_2$ greater than 456 ppm?"* If yes, human respiration confirms someone is inside!
- We deliberately set `max_depth=3`. Why? If you let a decision tree grow without depth limits, it creates hundreds of tiny, hyper-specific branches that memorize sensor noise. By capping depth at 3, the tree has at most $2^3 = 8$ final leaves. It is fast, clean, and impossible to overfit.

### Technique 2: Logistic Regression (With Feature Scaling)
Logistic Regression tries to draw a smooth multidimensional boundary line separating Empty from Occupied.
- **Why did we need `StandardScaler`?**  
  Look at the numbers: `Light` can be 800 Lux, `CO2` can be 1200 ppm, but `HumidityRatio` is around 0.0048 kg/kg! If you feed raw numbers into Logistic Regression without scaling, the model thinks `CO2` is 250,000 times more important than `HumidityRatio` simply because its numbers are bigger.  
  `StandardScaler` subtracts the mean and divides by standard deviation, giving every sensor a fair playing field centered at 0 with variance 1.

### Technique 3: Random Forest (The Ensemble Committee)
Instead of asking just one Decision Tree, Random Forest trains 100 independent decision trees on random subsets of the data and takes a democratic majority vote. This gives us our benchmark for maximum possible accuracy and allows us to calculate feature importance scores.

### Technique 4: Strict Chronological Splitting (Why Random K-Fold is Cheating!)
This was one of the biggest lessons of our project. In standard machine learning tutorials, people casually run `train_test_split(..., shuffle=True)` or 5-fold cross-validation.  
**Why is that completely wrong for sensor data?**
Because temperature and $\text{CO}_2$ do not teleport at random. If you measure $\text{CO}_2$ at 2:00 PM, the reading at 2:01 PM will be almost identical. If you randomly shuffle rows, 2:00 PM goes to training and 2:01 PM goes to validation! The model simply looks up its immediate temporal neighbor and claims 99.9% accuracy. That is **autocorrelation data leakage**.  
To prevent this, we took our training file and split it in **strict chronological order**:
- The first 75% in time (Feb 4 to Feb 8) was used for sub-training.
- The remaining 25% in time (Feb 8 to Feb 10) was used as the unseen validation set.

---

## 7. Our Real Results: What actually happened when we ran the code?

We ran our complete pipeline on our machine (`python run_all.py`). Below are the real, unedited numbers recorded in `outputs/tables/baseline_metrics.csv`:

### Table: Baseline Model Results on Both Test Conditions

| Model | Test Dataset | Accuracy | Precision | Recall (Crucial!) | F1-Score |
|---|---|---|---|---|---|
| **Decision Tree (depth=3)** | **Test 1 (Door Closed)** | **97.82%** | 94.80% | **99.49%** | 97.09% |
| **Decision Tree (depth=3)** | **Test 2 (Door Open)** | **97.67%** | 90.45% | **99.41%** | 94.72% |
| **Logistic Regression (Scaled)** | Test 1 (Door Closed) | 97.71% | 94.70% | 99.28% | 96.94% |
| **Logistic Regression (Scaled)** | Test 2 (Door Open) | 98.51% | 97.41% | 95.46% | 96.43% |
| **Random Forest (100 trees)** | Test 1 (Door Closed) | **97.82%** | 94.80% | **99.49%** | 97.09% |
| **Random Forest (100 trees)** | Test 2 (Door Open) | **99.30%** | 97.32% | **99.41%** | 98.36% |

### Why Recall is our favorite metric
Look closely at the table above. Why do we celebrate **Recall** over Accuracy?
- On Test 1, there were 972 occupied minutes. Our Decision Tree correctly caught **967 of them** (99.49% Recall). It missed only 5 minutes!
- On Test 2, there were 2,049 occupied minutes. Our Decision Tree caught **2,037 of them** (99.41% Recall). It missed only 12 minutes!
In a real office, a false positive just means the lights stay on for a bit longer. But a false negative turns the lights off while someone is sitting at their desk working. High recall means occupants are virtually never plunged into darkness.

### The Plain-Text Decision Tree Rules
When we exported the trained Decision Tree using `export_text()`, here is the exact tree that was generated:

```text
|--- Light <= 365.12 Lux
|   |--- Humidity <= 37.74 %
|   |   |--- Light <= 289.25 -> class: Empty (0)
|   |   |--- Light >  289.25 -> class: Empty (0)
|   |--- Humidity >  37.74 % -> class: Occupied (1)
|--- Light >  365.12 Lux
|   |--- CO2 <= 456.33 ppm
|   |   |--- Light <= 406.17 -> class: Occupied (1)
|   |   |--- Light >  406.17 -> class: Empty (0)
|   |--- CO2 >  456.33 ppm
|   |   |--- Temperature <= 22.21 -> class: Occupied (1)
|   |   |--- Temperature >  22.21 -> class: Occupied (1)
```

Look at how clear that is:
1. If Light is $\le 365$ Lux, the room is classified as **Empty**.
2. If Light is $> 365$ Lux, it checks $\text{CO}_2$. If $\text{CO}_2 > 456$ ppm, it is classified as **Occupied**.
3. If Light is high but $\text{CO}_2$ is low ($\le 456$ ppm), it flags the room as empty, catching the edge case where someone forgot the lights on or sunlight is shining in!

### Which sensors matter the most?
Our Random Forest feature importance analysis yielded:
1. **Light:** 55.4% importance
2. **$\text{CO}_2$:** 31.2% importance
3. **Temperature:** 8.7% importance
4. **HumidityRatio:** 3.1% importance
5. **Humidity:** 1.6% importance

Light and $\text{CO}_2$ account for **86.6%** of all predictive power!

---

## 8. Contribution 1: Our Sensor Ablation Study (Can we build this cheaper?)

We asked a practical question: *What if a college or company wants to install 500 of these boxes across campus and wants to cut costs? Which sensors can we remove?*

We ran two experiments on both test sets:
1. **Leave-One-Out:** Retraining after dropping one sensor at a time.
2. **Single-Sensor Models:** Training using only a single sensor.

### What the numbers proved:

```
+-------------------------------------------------------------------------------+
|                            ABLATION STUDY FINDINGS                            |
+-------------------------------------------------------------------------------+
| 1. LIGHT IS CRUCIAL:                                                          |
|    - Removing Light drops Test 2 recall from 99.41% down to 75.16%!           |
|    - "Only Light" alone gets 97.75% accuracy on Test 1 and 99.29% on Test 2.  |
|                                                                               |
| 2. CO2 IS VULNERABLE TO OPEN DOORS:                                           |
|    - "Only CO2" gets 86.87% accuracy when the door is closed (Test 1).        |
|    - But drops to 73.43% when the door is open (Test 2) because air diffuses! |
|                                                                               |
| 3. HUMIDITY IS 100% DISPENSABLE:                                              |
|    - Removing Humidity & HumidityRatio caused ZERO loss in accuracy or recall.|
|    - A deployment can eliminate humidity sensors entirely to save money.      |
+-------------------------------------------------------------------------------+
```

---

## 9. Contribution 2: Our Causal 5-Minute Trend Features

### The Physical Idea
When a person enters an empty room, their breath starts accumulating. $\text{CO}_2$ does not instantly jump to 1000 ppm; rather, its **rate of change** ($\frac{d\text{CO}_2}{dt}$) spikes upward! Similarly, when they leave, $\text{CO}_2$ slowly decays.  
Also, photodiode light sensors sometimes pick up momentary noise (like a cloud drifting across the sun for 10 seconds).

So we created two strictly backward-looking features:
1. `CO2_diff_5min`: $\text{CO}_2(t) - \text{CO}_2(t - 5)$ (rate of accumulation over the last 5 minutes).
2. `Light_mean_5min`: 5-minute rolling average of Light (temporal smoothing).

### The Causality Rule (Never Look Into the Future!)
We made sure our code only used past readings (`.shift(5)`). If you use a centered rolling window like `df['Light'].rolling(5, center=True)`, row $t$ averages readings from $t-2, t-1, t, t+1, t+2$. In a real building running on a Raspberry Pi or Arduino, you do not have $t+1$ and $t+2$! Doing that would be artificial cheating. Our code is 100% causal and real-time ready.

### How did we handle the first 4 minutes?
When a device is first switched on, there are no past 5 minutes:
- For `CO2_diff_5min`: We filled the first 4 rows with `0.0` (`fillna(0.0)`). Physical meaning: *Before we have 5 minutes of data, assume zero rate of change.*
- For `Light_mean_5min`: We used `rolling(window=5, min_periods=1).mean()`. Physical meaning: *At minute 1, use minute 1. At minute 2, average minutes 1 and 2.*  
Not a single row of data was thrown away.

### Did it work? (The Big Result!)
On **Test Set 2 (Door Open)**, where drafty air dilutes static $\text{CO}_2$ readings:
- **Baseline Decision Tree (raw sensors only):**
  - Accuracy: 97.67%
  - Precision: 90.45%
  - Recall: 99.41%
- **Trend-Enhanced Decision Tree (raw + 5-minute trends):**
  - Accuracy: **99.27%** (+1.60 percentage points!)
  - Precision: **97.05%** (+6.60 percentage points!)
  - Recall: **99.56%**

By adding just two simple 5-minute past features, our tiny 3-level Decision Tree reached **99.27% accuracy**, matching the 100-tree Random Forest! The physical rate-of-change feature gave the tree the dynamic velocity clue it needed to separate true occupancy from corridor air drafts.

---

## 10. The Gotchas & Edge Cases: When does our system struggle?

To be honest engineers, we must know exactly where our system has limitations:
1. **The "Forgotten Lights" Problem:** If the last person leaves an office at 6:00 PM and forgets to switch off the tube lights, `Light` stays high (>400 Lux). Because $\text{CO}_2$ takes 20 to 45 minutes to decay back to 400 ppm through natural ventilation, our system will think the room is occupied for about 20–30 minutes after they leave.
2. **Direct Afternoon Sunlight:** If direct sunlight streams through an unshaded window right onto the desk sensor, `Light` can read 500+ Lux even with artificial lights off. Our model uses $\text{CO}_2$ to catch this, but if someone is in the hallway breathing heavily near an open door, a false positive can occur.
3. **Seasonal Window Shift:** This dataset was collected in Mons, Belgium in February (winter). In the summer, people open windows, turn on table fans, and run air conditioners, which changes ventilation constants. A live system deployed across all 4 seasons would need periodic threshold re-calibration.

---

## 11. How Our Streamlit Web App Works

To make this project come alive, we built an interactive dashboard in `app.py`:
- **Interactive Sliders:** Users can move sliders for Light (0–1600 Lux), $\text{CO}_2$ (380–2200 ppm), Temperature (17–28 °C), and Humidity (15–50%).
- **Psychrometric Calculation:** The app calculates the exact physical `HumidityRatio` on the fly using the Magnus-Tetens thermodynamic equation.
- **Instant Inference:** It feeds the single row of numbers into our saved model (`occupancy_model.joblib`) and displays a big, clear status badge:
  - `🔴 ROOM STATUS: OCCUPIED` (with confidence percentage)
  - `🟢 ROOM STATUS: EMPTY` (with confidence percentage)
- **Pre-configured Presets:** We added quick preset buttons:
  - *Preset 1: Regular Working Hours (Occupied)* $\rightarrow$ 520 Lux, 950 ppm $\text{CO}_2$
  - *Preset 2: Empty Room at Night* $\rightarrow$ 0 Lux, 430 ppm $\text{CO}_2$
  - *Preset 3: Empty Room with Lights Left ON (Edge Case)* $\rightarrow$ 460 Lux, 420 ppm $\text{CO}_2$ (shows how low $\text{CO}_2$ correctly prevents a false positive!).

---

## 12. If we had another month, what would we build next?

If we were to take this project forward into our final year B.Tech capstone:
1. **Flash onto an ESP32 Microcontroller:** Since our best Decision Tree has only 8 leaf nodes, we can write a 30-line C `if-else` function and flash it directly onto a \$4 ESP32 or Raspberry Pi Pico running on battery power.
2. **Fuse with a \$1 PIR Sensor:** Pairing our ambient environmental model with a cheap PIR motion sensor solves the "forgotten lights" decay delay: the moment PIR sees zero motion for 10 minutes AND $\text{CO}_2$ is declining, the room is instantly declared Empty.
3. **Outdoor Baseline Normalization:** Placing one sensor outside the building to measure ambient outdoor $\text{CO}_2$ and sunlight, then subtracting outdoor values ($\Delta\text{CO}_2 = \text{CO}_{2,\text{indoor}} - \text{CO}_{2,\text{outdoor}}$), making the model immune to seasonal weather shifts.

---

## 13. Summary & Conclusion: What did we learn?

Building this project taught us three key lessons that classroom theory rarely shows:
1. **Clarity beats cleverness:** We do not need massive, mysterious models for every problem. A clean 3-level Decision Tree achieved 97.8% baseline accuracy and 99.49% recall because the physics of the problem (lights turned on, human breathing) creates crisp step boundaries.
2. **Domain knowledge matters more than fancy algorithms:** Adding two simple physical trend features ($\Delta\text{CO}_2$ and rolling light mean) did more for open-door accuracy (+1.6% accuracy, +6.6% precision) than switching between different machine learning algorithms.
3. **Data hygiene is non-negotiable:** Checking the raw file formatting, verifying the 1-minute sampling interval, and using strict chronological validation splits prevented the subtle data leakages that trip up many student projects.

Everything we built—from automated data loading and exploratory plots to ablation studies, trend models, and the Streamlit web demo—runs cleanly and reproducibly with a single command:
```bash
python run_all.py
```

---
*Report prepared by 2nd-Year B.Tech Students, Department of Computer Science & Engineering, IIIT Bhopal.*
