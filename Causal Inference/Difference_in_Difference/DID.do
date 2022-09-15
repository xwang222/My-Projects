clear all
causaldata organ_donations.dta, use clear

gen TreatedGroup = 0
gen AfterTreatment = 0

replace TreatedGroup = 1 if state=="California"
replace AfterTreatment = 1 if quarter_num >=4
gen Treat_After = TreatedGroup*AfterTreatment

gen lag_1=0
gen lag_2=0
gen lag_3=0
gen lead_0=0
gen lead_1=0
gen lead_2=0

replace lag_3=1 if state=="California" & quarter_num ==1
replace lag_2=1 if state=="California" & quarter_num ==2
replace lag_1=1 if state=="California" & quarter_num ==3
replace lead_0=1 if state=="California" & quarter_num ==4
replace lead_1=1 if state=="California" & quarter_num ==5
replace lead_2=1 if state=="California" & quarter_num ==6

encode state, gen(n_s)
encode quarter, gen(n_q)

gen treated = 0
replace treated = 1 if state=="California" & quarter_num >=4

gen placebo_sample_t = 1 if quarter_num <=3
gen treat_placebo_t = 0
replace treat_placebo_t =1 if state=="California" & quarter_num >=3

gen placebo_sample_s = 1 if state !="California" 
gen treat_placebo_s = 0
replace treat_placebo_s =1 if state=="New York" & quarter_num >=4


* Estimation of Treatment effect
reg rate treated i.n_s i.n_q , vce(cluster state)

* Placeo test - time
reg rate treat_placebo_t i.n_s i.n_q if placebo_sample_t == 1, vce(cluster state)

* Placeo test - state
reg rate treat_placebo_s i.n_s i.n_q if placebo_sample_s == 1, vce(cluster state)

* Event study specification
reg rate lag_2 lag_3 lead_0 lead_1 lead_2 i.n_s i.n_q , vce(cluster n_s)

scalar b1 = _b[lag_3] 
scalar b2 = _b[lag_2] 
scalar b3 = _b[lead_0] 
scalar b4 = _b[lead_1] 
scalar b5 = _b[lead_2] 

scalar se1 = _se[lag_3] 
scalar se2 = _se[lag_2] 
scalar se3 = _se[lead_0] 
scalar se4 = _se[lead_1] 
scalar se5 = _se[lead_2] 


gen coef = 0
replace coef = b1 if quarter_num ==1
replace coef = b2 if quarter_num ==2
replace coef = b3 if quarter_num ==4
replace coef = b4 if quarter_num ==5
replace coef = b5 if quarter_num ==6

gen ste = 0 
replace ste = se1 if quarter_num ==1
replace ste = se2 if quarter_num ==2
replace ste = se3 if quarter_num ==4
replace ste = se4 if quarter_num ==5
replace ste = se5 if quarter_num ==6

gen lb=0
replace lb = coef-1.96*ste

gen ub=0
replace ub = coef+1.96*ste

keep if n_s==1

twoway (sc coef quarter_num, connect(line)) ///
  (rcap ub lb quarter_num) ///
    (function y = 0, range(1 6)), xline(3, lstyle(grid)) xtitle("Quarter") ///
    caption("95% Confidence Intervals Shown") leg(off)

