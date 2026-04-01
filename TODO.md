# TODO: Fix TypeError '<=' not supported between str and int

**Completed Steps:**
1. [x] Ensure all numeric columns converted on CSV load: pd.to_numeric(errors='coerce'), fillna(0).
2. [x] Fix register_number handling in profile.
3. [x] Reset index after load.
4. [x] Convert df['id'], users_df['id'] to numeric.
5. [x] Sort df by id descending.
6. [x] Update admin complaints view to sort by timestamp desc (show recent first).

# Task Complete: TypeError fixed by ensuring safe numeric conversions on CSV load and displays.

All steps completed successfully. Changes ensure no str vs int comparisons in pandas operations or displays.
