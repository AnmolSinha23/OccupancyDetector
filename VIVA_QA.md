# Viva Voce Examination Cheat Sheet: Room Occupancy Detection

**Course:** CSE-3006 Advanced Programming Lab (Python)  
**Department of Computer Science & Engineering, IIIT Bhopal**  
**Project Topic:** Room Occupancy Detection from Environmental Sensors  
**Paper Reference:** Candanedo & Feldheim (*Energy and Buildings*, 2016)

---

## ⏱️ Section 1: "Explain Each Script in 30 Seconds" (Rapid Viva Intro)

When the examiner points at any file in your project folder, deliver these exact 30-second explanations:

### 1. `src/data_loading.py`
> *"Sir, this script downloads the UCI Occupancy Detection dataset (UCI ID 357) via `ucimlrepo` or fallback direct zip. It parses timestamps into datetime objects, sorts chronologically, verifies data types, and prints class balance. In our training set of 8,143 rows, 78.8% are Empty and 21.2% are Occupied, with zero missing values."*

### 2. `src/exploration.py`
> *"This script generates our three exploratory plots: time-series of Light and CO2 over time, class balance across all splits, and a sensor correlation heatmap. It visually proves that Light and CO2 jump synchronously whenever humans enter the room, establishing them as our primary predictor candidates."*

### 3. `src/baseline_models.py`
> *"Here we train our three baseline models: a readable Decision Tree with max_depth=3, a scaled Logistic Regression pipeline, and a Random Forest. It evaluates both test files separately, prints the metrics table, saves confusion matrices, plots Random Forest feature importance, and exports human-readable decision rules using `export_text()`."*

### 4. `src/sensor_ablation.py`
> *"This is our first original contribution. We systematically ablate sensors in two ways: removing one sensor at a time (leave-one-out) and training models on single sensors. It proves that Light is dominant (removing it drops recall from 99.4% to 75.2% on Test 2), while Humidity and HumidityRatio are completely redundant and can be omitted to save hardware costs."*

### 5. `src/trend_features.py`
> *"This is our second original contribution. Live IoT systems cannot see the future. We first verified the data sampling interval is 1 minute, then engineered causal 5-minute past differences ($\Delta\text{CO2}$) and 5-minute rolling Light means using strictly past readings (`.shift(5)`). This boosted Decision Tree accuracy on the open-door test set from 97.67% to 99.27%."*

### 6. `src/hyperparameter_tune.py`
> *"This script tunes `max_depth` using a strict chronological split (first 75% sub-train, last 25% validation). We never use random k-fold because temporal autocorrelation would cause data leakage. We found `max_depth=3` achieves 99.8% validation recall while deeper trees (depth=10) overfit and crash to 17.8% recall."*

### 7. `src/optional_boosting.py`
> *"This script trains `HistGradientBoostingClassifier` as an optional modern reference. It bins continuous features into 256 histograms for fast sequential boosting. It achieves ~92-94% accuracy, but we show that our transparent Decision Tree actually outperforms it (97.8%) because occupancy follows sharp step thresholds."*

### 8. `app.py`
> *"This is our Streamlit web demo. It loads our trained, explainable decision tree and takes real-time inputs for Light, CO2, Temperature, and Humidity via sliders. It automatically computes physical `HumidityRatio` and displays an instant OCCUPIED or EMPTY badge with confidence percentage and rule explanation."*

### 9. `run_all.py`
> *"This is our master convenience script. Running `python run_all.py` executes all pipeline stages end-to-end in 15 seconds, creating all CSV tables and figures in `outputs/` without any manual intervention."*

---

## 🎓 Section 2: Top 20 Viva Questions & Model Answers

### Q1. Why did you choose environmental sensors instead of a camera or PIR motion sensor?
**Answer:**  
Cameras invade personal privacy, violate privacy regulations (like GDPR) in private offices, and require power-hungry video processing. Passive Infrared (PIR) sensors only detect motion—if an occupant sits still reading or typing, PIR reports false vacancy. Environmental sensors (Light, CO2, Temperature) are privacy-preserving, inexpensive, low-power, and reliably detect presence even when occupants are completely stationary.

---

### Q2. What is the physical principle behind each sensor? Why do they work?
**Answer:**  
1. **Light (Lux):** Humans turn artificial lighting on during occupancy. Indoor light jumps from <10 Lux (dark) to 300–600 Lux (illuminated).
2. **CO2 (ppm):** Human lungs exhale ~40,000 ppm of carbon dioxide. In an enclosed office, exhaled breath drives ambient CO2 from ~400 ppm (outdoor baseline) up to 700–1,500+ ppm.
3. **Temperature & Humidity:** The human body emits sensible metabolic heat (~100 Watts) and water vapor, subtly elevating room temperature and humidity ratio.

---

### Q3. Why did you choose Decision Tree, Random Forest, and Logistic Regression?
**Answer:**  
- **Decision Tree (`max_depth=3`):** It gives 100% white-box explainability. We can trace every prediction by hand using simple IF-THEN rules on Light and CO2 thresholds.
- **Random Forest:** It reduces prediction variance through bootstrap bagging and ensemble voting, serving as our robust non-linear benchmark.
- **Logistic Regression:** It provides a simple linear probabilistic baseline with continuous sigmoid confidence, trained with feature scaling.

---

### Q4. What is the difference between Accuracy, Precision, and Recall in this specific problem?
**Answer:**  
- **Accuracy:** Total correct classifications over total samples. Can be misleading due to class imbalance (~79% empty).
- **Precision ($\frac{TP}{TP + FP}$):** When the model claims the room is *Occupied*, how often is someone actually there?
- **Recall ($\frac{TP}{TP + FN}$):** Out of all actual occupied minutes, what percentage did the system successfully catch?

---

### Q5. Why is Recall the most critical metric for occupancy detection?
**Answer:**  
Because the operational costs of errors are asymmetric:
- **False Positive:** Room is empty, but predicted occupied. Result: Lights or ventilation stay on slightly longer (minor energy penalty).
- **False Negative:** Room is occupied, but predicted empty. Result: Lights shut off and ventilation stops while people are actively working (major safety, comfort, and productivity violation).  
Therefore, we must maximize **Recall** so that occupied rooms are almost never missed.

---

### Q6. What were your actual baseline results on the test sets?
**Answer:**  
On **Test Set 1 (Door Closed)**:
- Decision Tree (`max_depth=3`): **97.82% Accuracy**, **99.49% Recall**, 97.09% F1-Score.
- Random Forest: **97.82% Accuracy**, **99.49% Recall**, 97.09% F1-Score.
- Logistic Regression: 97.71% Accuracy, 99.28% Recall.

On **Test Set 2 (Door Open)**:
- Decision Tree: **97.67% Accuracy**, **99.41% Recall**.
- Random Forest: **99.30% Accuracy**, **99.41% Recall**.

---

### Q7. Why are there two separate test files (`datatest.txt` and `datatest2.txt`)?
**Answer:**  
They represent different physical environments:
- In `datatest.txt` (Test 1), the office door was kept **closed**, identical to the training conditions.
- In `datatest2.txt` (Test 2), the office door was left **mostly open**.  
Having both allows us to test **environmental domain shift**—how well a model trained in a closed room performs when hallway airflow disperses CO2.

---

### Q8. What does your Sensor Ablation Study show? What is your first contribution?
**Answer:**  
Our ablation study tested leave-one-out and single-sensor subsets:
1. **Light is vital:** Removing Light causes Test 2 recall to crash from **99.41% down to 75.16%**. "Only Light" alone gets **97.75%** accuracy on Test 1.
2. **CO2 is vulnerable to open doors:** "Only CO2" achieves 86.87% accuracy when the door is closed, but drops to **73.43%** when the door is open due to hallway air dilution.
3. **Humidity is redundant:** Removing Humidity or HumidityRatio causes **0.0% loss** in accuracy or recall. A production hardware device can safely omit humidity sensors to cut costs.

---

### Q9. What are Trend Features, and why did you use ONLY past readings?
**Answer:**  
This is our second contribution. A live edge microcontroller running in real time cannot see future timestamps ($t+1$). Using centered rolling windows or future shifts creates **look-ahead data leakage**.  
We created two strictly causal features:
1. `CO2_diff_5min`: $\text{CO}_2(t) - \text{CO}_2(t-5)$, measuring the physical slope of human exhalation buildup.
2. `Light_mean_5min`: 5-minute rolling average, filtering transient photodiode flickers.

---

### Q10. What was the sampling interval of the dataset, and how did you verify it?
**Answer:**  
We verified the sampling interval by computing `df['date'].diff()`. The mode interval across all three datasets is **exactly 60 seconds (1 minute)**. Therefore, a 5-minute historical window corresponds strictly to **5 rows** (`.shift(5)`).

---

### Q11. How did you handle the boundary rows (first 4 rows) where 5-minute history is missing?
**Answer:**  
- For `CO2_diff_5min`, we imputed missing lag rows with `0.0` using `.fillna(0.0)`. Physically, before 5 minutes of history exist, we assume a neutral rate of change.
- For `Light_mean_5min`, we used `rolling(window=5, min_periods=1).mean()`, which computes the running average of available historical rows without creating NaNs.  
No rows were dropped, preserving 100% of test samples.

---

### Q12. Did trend features improve model performance?
**Answer:**  
Yes! On the challenging Door-Open test set (Test 2), adding 5-minute trend features boosted our Decision Tree accuracy from **97.67% to 99.27%** (+1.60 percentage points) and precision from **90.45% to 97.05%** (+6.60 percentage points), matching the 100-tree Random Forest while maintaining 99.56% recall.

---

### Q13. Why did you use a chronological validation split instead of Random K-Fold Cross-Validation?
**Answer:**  
Sensor telemetry is continuous time-series data with strong autocorrelation—a reading at 10:00 AM is almost identical to 10:01 AM. If you randomly shuffle rows into cross-validation folds, adjacent minutes leak into both training and validation sets. The model cheats by memorizing nearest neighbors (temporal data leakage). A strict chronological split (first 75% sub-train, last 25% validation) evaluates true future generalization.

---

### Q14. What happened during hyperparameter tuning of `max_depth`?
**Answer:**  
Using our chronological validation split:
- At `max_depth=3`, sub-train accuracy was 98.71% and validation recall was **99.83%**.
- At `max_depth=10`, sub-train accuracy reached 99.97% (overfitting), but validation accuracy crashed to **69.11%** and validation recall plummeted to **17.86%**.  
This proved to us empirically that keeping `max_depth=3` prevents leaf-level noise memorization.

---

### Q15. Can you walk through the Decision Tree rules extracted by `export_text()`?
**Answer:**  
Yes, the tree has 3 levels:
1. **Root Split:** `Light <= 365.12 Lux`. If Light is low, check Humidity: if Humidity $\le 37.7\%$, predict **EMPTY** (~99% of dark rooms).
2. **Right Branch (Light > 365 Lux):** Check `CO2 <= 456.33 ppm`.
3. If CO2 is high (>456 ppm), human respiration confirms **OCCUPIED**. If CO2 is low despite bright light, it detects the edge case where sunlight enters an empty room.

---

### Q16. What is `HistGradientBoostingClassifier`, and how did it perform?
**Answer:**  
It is scikit-learn's implementation of histogram-based gradient boosting (similar to LightGBM). It bins continuous values into 256 integer bins and trains trees sequentially to predict previous errors.  
In our tests, it achieved **91.97%** on Test 1 and **94.06%** on Test 2 with ~83–85% recall. It achieved lower recall than our Decision Tree (99.4%) because it slightly overfitted subtle temperature/humidity fluctuations rather than sticking to the clean Light/CO2 step boundary.

---

### Q17. How does your Streamlit web demo in `app.py` work?
**Answer:**  
`app.py` loads our trained explainable Decision Tree (`outputs/models/occupancy_model.joblib`). It provides sliders for Light, CO2, Temperature, and Humidity. It uses the Magnus-Tetens formula to compute `HumidityRatio` dynamically, passes the single-row vector to the model, and displays `🔴 OCCUPIED` or `🟢 EMPTY` with predicted probability and rule explanation.

---

### Q18. What are the key limitations of this project and dataset?
**Answer:**  
1. **Single Office Environment:** Data was recorded in one 3.1m × 5.8m room in Belgium; thresholds may shift in large open-plan spaces.
2. **Winter Window:** Collected over two weeks in February 2015; summer HVAC or open windows would alter baseline temperature and humidity.
3. **Lights Left ON:** If an occupant leaves lights on in an empty room, the model must wait for CO2 to dissipate (takes 20–40 minutes) before detecting vacancy.
4. **Sunlight Saturation:** Strong direct sunlight through exterior windows can illuminate the light sensor even if artificial lights are off.

---

### Q19. What would you do next to improve this project?
**Answer:**  
1. **Hardware Microcontroller Port:** Export the depth-3 decision tree to C/C++ using `micromlgen` to run on an ultra-low-power ESP32 or Raspberry Pi Pico.
2. **PIR Sensor Fusion:** Add a cheap PIR motion sensor as an instant interrupt to eliminate the CO2 decay latency when occupants leave.
3. **Outdoor Baseline Normalization:** Subtract outdoor ambient CO2 and solar lux in real time to handle seasonal weather shifts.

---

### Q20. If I slide Light to 0 and push CO2 high on the demo, the model says EMPTY. Wouldn't one assume someone is sleeping in the dark? Why is the model showing EMPTY?
**Answer:**  
*"Sir, that is a fantastic edge-case question! There are three core reasons backed by real data:*  
1. **Domain Context (Office vs. Bedroom):** This dataset and model are specifically trained for **commercial office rooms**, not residential bedrooms. People do not sleep in pitch-black darkness during office working hours.  
2. **CO2 Ventilation Lag (The True Physical Reason):** In an office, workers leave at 6:00 PM, switch off the lights (Light = 0 Lux), and go home. However, exhaled CO2 does not disappear instantly—it takes 30 to 60 minutes to slowly leak out of the room.  
3. **Ground-Truth Data Evidence:** Across the training and test datasets, there are **3,233 real measurements** where Light was < 10 Lux and CO2 was > 650 ppm. In **100% of those 3,233 cases**, the ground-truth camera confirmed the room was completely EMPTY! If our model predicted 'Occupied' here, it would create false alarms every single evening, wasting electricity by running AC in empty offices.  
*Note: To detect someone sleeping in a home bedroom, our second contribution (5-minute trend features) is needed: if someone is sleeping, CO2 is actively rising ($\Delta\text{CO}_2 > 0$); if the room is empty after hours, CO2 is falling ($\Delta\text{CO}_2 < 0$)."*

---

### Q21. In one sentence, what is your team's core contribution over the original paper?
**Answer:**  
*"While Candanedo & Feldheim showed statistical models can detect occupancy, we proved through ablation that humidity is redundant, demonstrated that causal 5-minute past trend features boost open-door decision tree accuracy to 99.27%, and packaged the pipeline into a fully explainable, leak-free, interactive application."*
