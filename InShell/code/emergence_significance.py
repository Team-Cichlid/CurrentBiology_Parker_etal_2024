emergence <- read.csv('emergence_time.csv')

model <- lm(emergence_time ~ day_of_removal + cross_foster, data=emergence)

summary(model)

Call: lm(formula = emergence_time ~ day_of_removal + cross_foster, data = emergence) 
Residuals: Min 1Q Median 3Q Max -1.1461 -0.4162 -0.2178 0.2546 1.3097 
    Coefficients: Estimate Std. Error t value Pr(>|t|) 
(Intercept) 4.71072 0.71832 6.558 1.83e-05 *** 
day_of_removal 0.47708 0.07743 6.161 3.42e-05 *** 
cross_foster 0.30413 0.16344 1.861 0.0855 . --

- Signif. codes: 0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1 Residual standard error: 0.723 on 13 degrees of freedom Multiple R-squared: 0.7721, Adjusted R-squared: 0.737 F-statistic:
22.02 on 2 and 13 DF, p-value: 6.697e-05 