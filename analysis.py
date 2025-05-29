import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.cm as cm
import numpy as np

# --- 1. Load Gaze Data ---
with open('gazeData.json', 'r') as f:
    gaze_data = json.load(f)

if not gaze_data:
    print("No gaze data found.")
    exit()

df = pd.DataFrame(gaze_data)
df['timestamp'] = df['timestamp'] - df['timestamp'].min()

# --- 2. Plot Heatmap ---
plt.figure(figsize=(10, 6))
sns.kdeplot(x=df['x'], y=df['y'], fill=True, cmap=cm.get_cmap('jet'), thresh=0.05)
plt.title("Eye Gaze Heatmap")
plt.gca().invert_yaxis()
plt.show()

# --- 3. Detect Fixations (I-DT method) ---
FIXATION_RADIUS = 50  # pixels
FIXATION_DURATION = 100  # milliseconds

fixations = []
i = 0

while i < len(df):
    j = i + 1
    while j < len(df):
        window = df.iloc[i:j+1]
        dx = window['x'].max() - window['x'].min()
        dy = window['y'].max() - window['y'].min()
        duration = window['timestamp'].iloc[-1] - window['timestamp'].iloc[0]

        if dx <= FIXATION_RADIUS and dy <= FIXATION_RADIUS and duration >= FIXATION_DURATION:
            j += 1
        else:
            break

    if j - i > 1:
        fixation_window = df.iloc[i:j]
        fix_x = fixation_window['x'].mean()
        fix_y = fixation_window['y'].mean()
        start_time = fixation_window['timestamp'].iloc[0]
        end_time = fixation_window['timestamp'].iloc[-1]
        fixations.append({'x': fix_x, 'y': fix_y, 'start': start_time, 'end': end_time})
        i = j
    else:
        i += 1

fix_df = pd.DataFrame(fixations)

# --- 4. Visualize Fixation Points & Sequence ---
plt.figure(figsize=(10, 6))
plt.scatter(fix_df['x'], fix_df['y'], c='red', s=80, label='Fixations')

for i in range(1, len(fix_df)):
    x_values = [fix_df.iloc[i-1]['x'], fix_df.iloc[i]['x']]
    y_values = [fix_df.iloc[i-1]['y'], fix_df.iloc[i]['y']]
    plt.plot(x_values, y_values, color='black', linestyle='--', linewidth=1)

for i, (x, y) in enumerate(zip(fix_df['x'], fix_df['y'])):
    plt.text(x + 5, y - 5, str(i+1), fontsize=9, color='blue')

plt.title("Fixation Sequence with Lines")
plt.legend()
plt.gca().invert_yaxis()
plt.show()

print("Detected Fixations:")
print(fix_df[['x', 'y', 'start', 'end']])

# --- 5. Calculate Saccadic Distances and Velocities ---
saccade_distances = []
saccade_durations = []

for i in range(1, len(fix_df)):
    x1, y1 = fix_df.iloc[i-1]['x'], fix_df.iloc[i-1]['y']
    x2, y2 = fix_df.iloc[i]['x'], fix_df.iloc[i]['y']
    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    duration = fix_df.iloc[i]['start'] - fix_df.iloc[i-1]['end']

    saccade_distances.append(distance)
    saccade_durations.append(duration / 1000)  # in seconds

# --- Compute Averages ---
if saccade_distances:
    avg_distance = np.mean(saccade_distances)
    avg_velocity = np.mean(np.array(saccade_distances) / np.array(saccade_durations))
    avg_density = len(saccade_distances) / (df['timestamp'].iloc[-1] / 1000)

    print(f"\n\uD83D\uDCCF Average Saccadic Distance: {avg_distance:.2f} pixels")
    print(f"⚡ Average Saccadic Velocity: {avg_velocity:.2f} pixels/sec")
    print(f"📈 Average Saccadic Density: {avg_density:.2f} saccades/sec")

    plt.figure(figsize=(8, 5))
    plt.hist(saccade_distances, bins=10, color='skyblue', edgecolor='black')
    plt.title("Histogram of Saccadic Distances")
    plt.xlabel("Distance (pixels)")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()
else:
    print("Not enough fixations to compute saccades.")

# --- Export Fixation Data ---
fix_df.to_csv("fixations.csv", index=False)

# --- Export Saccade Data ---
if saccade_distances:
    saccade_df = pd.DataFrame({
        'from_x': fix_df['x'][:-1].values,
        'from_y': fix_df['y'][:-1].values,
        'to_x': fix_df['x'][1:].values,
        'to_y': fix_df['y'][1:].values,
        'distance': saccade_distances,
        'duration_sec': saccade_durations
    })
    saccade_df.to_csv("saccades.csv", index=False)
else:
    saccade_df = pd.DataFrame()

# --- Export Summary Report ---
with open("gaze_summary_report.txt", "w") as f:
    f.write("Eye Tracking Summary Report\n")
    f.write("===============================\n\n")
    f.write(f"Total Gaze Points: {len(df)}\n")
    f.write(f"Total Fixations: {len(fix_df)}\n")
    if not saccade_df.empty:
        f.write(f"Average Saccadic Distance: {avg_distance:.2f} pixels\n")
        f.write(f"Average Saccadic Velocity: {avg_velocity:.2f} pixels/sec\n")
        f.write(f"Average Saccadic Density: {avg_density:.2f} saccades/sec\n")
    else:
        f.write("Not enough saccades for analysis.\n")
    f.write("\nFixations exported to: fixations.csv\n")
    f.write("Saccades exported to: saccades.csv\n")
