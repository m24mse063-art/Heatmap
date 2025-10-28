It must only use the statewise monthly data provided in our Excel / CSV sheets.
No hallucination, no synthetic data, no projections.

1. Data Ingestion Rules
Source of truth

We ingest from the provided indicator files only. Examples (exact file names we received):

CPI_Combined .csv

CPI_Rural .csv

CPI_Urban .csv

CMIE unemp rate.csv

STATEWISE NEW PAYROLL DATA (EPF.csv

Job_Data .csv

Job Data _nos.csv

Credit saturation (In Rs cr) .csv

Credit saturation (%.csv

Statewise deposits in SCBs .csv

Statewise deposits in SCBs(%) .csv

FDI_EQUITY INFLOwS Oct 2019 (cr.csv

Gst Collection (In Cr) .csv

Gst Collection (% growth) .csv

Vehicle Sale(Nos) -all vehicle.csv

2W sales Nos.csv

tractor sales count .csv

Freight (in Metric Tonne).csv

AIRCRAFT MOVEMENTS (IN NOS).csv

Passenger Traffic(nos).csv

lessthan60.csv / lessthan60.xlsx

60 sq.mt.-110.csv

greaterthan110.csv

Composite Prices .csv

Transform into a single long table

All individual files must be reshaped into ONE normalized table with columns:

| dataset | category | state | date | value | yoy_pct |

Definitions:

dataset = short machine id for the indicator. Example:

cpi_combined, cpi_rural, cpi_urban

unemployment_rate

epf_payroll

naukri_job_abs, naukri_job_growth_pct

credit_outstanding_inr, credit_saturation_pct, bank_deposits_inr, deposit_share_pct, fdi_equity_inflows

gst_collection_inr, gst_growth_pct, vehicle_sales_all, vehicle_sales_2w, tractor_sales, freight_volume, aircraft_movements, passenger_traffic

housing_lt60, housing_60_110, housing_gt110, housing_composite_index

category = macro bucket we show in the UI. Must be one of:

"Prices & Inflation Dynamics"

"Labour Market & Payroll Activity"

"Banking, Investment, Credit & Financial Depth"

"Consumption & Domestic Demand"

"Housing & Real Estate"

state = state/UT name exactly as in the source file. Do not rename without approval.

date = month truncated to first of month (YYYY-MM-01). Do not guess missing months.

value = numeric level from the sheet for that (dataset, state, date).

Example: GST collection amount in ₹ Cr.

Example: unemployment rate %.

Example: job postings absolute count.

Example: aircraft movements.

yoy_pct = Year-over-Year % growth for that (dataset, state):

yoy_pct = ((value_t - value_t-12) / abs(value_t-12)) * 100


If there isn’t 12 months of history, leave it null. Do NOT forward fill. Do NOT smooth.

Special case:

Some sheets already store a growth rate (e.g. Gst Collection (% growth) .csv, Naukri growth %).

For those, store their numeric value as value.

Still also compute yoy_pct using the rule above so we’re consistent across charts.

This unified, long-form table is the ONLY dataset the dashboard front end should consume.
Store it in:

a Supabase table (macro_master, columns above), OR

a bundled CSV (y_macro_master_with_yoy.csv) in public/data/ during early dev.

No other shadow transforms.

2. Category Mapping (Don’t improvise this)

Every dataset must map to exactly one of these high-level dashboard categories:

Prices & Inflation Dynamics

cpi_combined

cpi_rural

cpi_urban

Labour Market & Payroll Activity

epf_payroll

naukri_job_abs (Naukri absolute job postings count)

naukri_job_growth_pct (Naukri % change)

unemployment_rate

Banking, Investment, Credit & Financial Depth

credit_outstanding_inr

credit_saturation_pct

bank_deposits_inr

deposit_share_pct

fdi_equity_inflows

Consumption & Domestic Demand

gst_collection_inr

gst_growth_pct

vehicle_sales_all

vehicle_sales_2w

tractor_sales

freight_volume

aircraft_movements

passenger_traffic

Housing & Real Estate

housing_lt60

housing_60_110

housing_gt110

housing_composite_index (composite housing median across segments)

Note:

"Composite Prices .csv" is NOT inflation category. It contributes to housing_composite_index under “Housing & Real Estate.”

Do not add any “All-India total” unless such a row explicitly exists in the source file.

3. Front-End Dashboard Rules

The dashboard has global filters in the header:

Category (single select; defaults to "Prices & Inflation Dynamics")

Indicator / Dataset (multi-select but scoped to chosen category)

State (multi-select, up to 5 states max for line charts)

Date range (month range filter)

Value Metric toggle:

“Level” = use value

“YoY %” = use yoy_pct

Light / Dark mode toggle

Visual tabs / pages
A. Trend Over Time

Type: time-series line chart.

X-axis: date.

Y-axis: either value or yoy_pct based on the toggle.

Series: each selected state is its own line.

Limit: plot at most 5 states. If >5 selected, plot first 5 and show a warning like “Showing first 5 states”.

No smoothing, no interpolation across missing data, no forward projections.

B. Cross-State Snapshot

Type: bar chart.

Show latest available month (most recent date that has data for that dataset).

One bar per state.

Sort rule:

For unemployment rate, lower = better, so sort ascending.

For everything else, higher = better, so sort descending.

Bars should label numeric value.

Use either value or yoy_pct depending on the same global toggle.

C. Heatmap

Type: heatmap (state vs date).

Color = yoy_pct (diverging around 0).

X-axis = time (month).

Y-axis = state.

Only display yoy_pct here; not value.

D. State Drilldown

Select ONE state.

Show a vertical stack of mini time-series line charts — one per dataset in the chosen category — for that one state.

X-axis: date.

Y-axis: either value or yoy_pct (follow global toggle).

Only render charts for datasets that have data for that state.

E. Bubble View (conditional)

Scatter/bubble plot for a chosen single month.

X-axis: credit_saturation_pct (Banking/Investment/Credit & Financial Depth).

Y-axis: gst_growth_pct (Consumption & Domestic Demand).

Bubble size: unemployment_rate or epf_payroll (Labour).

Color: category color or sign of growth.

One bubble = one state.

Only render this chart if we have ≥10 states with all required fields for the selected month. Otherwise show message “Not enough comparable data this month.”

Never fabricate missing values for a state.

Dark / Light mode

Must be user-toggleable.

Use Tailwind dark mode classes (or similar).

In dark mode: dark background, muted gridlines, high-contrast text, but keep positive/negative color logic readable.

4. Behavior Rules / Guardrails

Do NOT invent or backfill missing months. If a line has a gap, leave a visible break.

Do NOT compute moving averages, “momentum scores,” or any composite index unless explicitly defined in this README.

Do NOT generate or display an “India average” unless the row “India” (or “All India”) exists in that sheet.

Do NOT rename states programmatically (e.g., “NCT of Delhi” → “Delhi”) without approval, because that breaks YoY matching.

All YoY math is 12-month lag. Do not change lag window.

5. Folder / Code Structure Guidance

Recommended structure (you can enforce in repo):

/data_raw/           # all original csv/xlsx files as provided
/data_processed/     # generated y_macro_master_with_yoy.csv
/src/data/ingest/    # ETL scripts: reshape, merge, compute yoy_pct
/src/data/constants/ # category mapping, dataset IDs, color assignments
/src/hooks/          # React hooks (e.g. useFilteredData, useDarkMode)
/src/components/     # Chart components, FilterBar, StateSelector, etc.

Key React expectations:

Use Recharts LineChart, BarChart, ScatterChart (bubble).

Global filter state should be maintained in context or a top-level provider so all tabs react consistently to user choices.

Max 5 states logic is enforced at the chart component level.

6. Developer Checklist (PRs must satisfy)

Any PR must:

Use only the merged master dataset columns (dataset, category, state, date, value, yoy_pct) as defined here.

Respect the 5-state max in comparison charts.

Use 12-month YoY for growth.

Respect category → dataset mapping defined above. No ad-hoc buckets.

Support dark mode toggle in the header.

Not introduce external data sources without sign-off.

If any of those are violated, the PR is out of spec.

TL;DR for engineers

All backend ETL must output one master long-form table with dataset, category, state, date, value, yoy_pct.

All charts read only from that table.

Dashboard tabs are: Trend Over Time, Cross-State Snapshot, Heatmap, State Drilldown, Bubble View.

Up to 5 states visible at once.

Dark mode required.

No fake data, no projections, no smoothing.
