"use client";
import React, { useState, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { getDailyGain, fetchAccountData, getTradeHistory, getDataDaily } from "@/lib/myFxbookApi";
import { groupDailyGainByWeek } from "@/lib/profit-helpers";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Calculator, TrendingUp, BarChart3, Zap, Target, Brain } from "lucide-react";

const formatCurrency = (value: any) => {
  if (typeof value === "number") {
    return `$${new Intl.NumberFormat("en-US").format(value)}`;
  }
  return value;
};

interface CalculationMethod {
  name: string;
  icon: React.ReactNode;
  description: string;
  daysToDouble: number | null;
  confidence: number;
  details: {
    assumptions: string[];
    calculations: string[];
    factors: string[];
    limitations: string[];
  };
}

const ProfitPrediction = () => {
  const [timeframe, setTimeframe] = useState(6);
  const [showCalculations, setShowCalculations] = useState(false);
  const defaultStartDate = "01/01/2000";
  const defaultEndDate = "01/31/2032";
  const session = process.env.NEXT_PUBLIC_MFX_SESSION || "";
  const searchParams = useSearchParams();
  const id = searchParams?.get("id") || "11405738";

  // Fetch all required data
  const { data: dailyGain, isLoading: isDailyGainLoading } = useQuery({
    queryKey: ["dailyGain", session, id],
    queryFn: () => getDailyGain(session, id, defaultStartDate, defaultEndDate),
    enabled: !!session && !!id,
  });

  const { data: accountData, isLoading: isAccountLoading } = useQuery({
    queryKey: ["accountData", session, id],
    queryFn: () => fetchAccountData(session, Number(id)),
    enabled: !!session && !!id,
  });

  const { data: tradeHistory, isLoading: isTradeHistoryLoading } = useQuery({
    queryKey: ["tradeHistory", session, id],
    queryFn: () => getTradeHistory(session, id),
    enabled: !!session && !!id,
  });

  const { data: dataDaily, isLoading: isDataDailyLoading } = useQuery({
    queryKey: ["dataDaily", session, id],
    queryFn: () => getDataDaily(session, id, defaultStartDate, defaultEndDate),
    enabled: !!session && !!id,
  });

  const weeklyData = dailyGain ? groupDailyGainByWeek(dailyGain) : [];

  // Enhanced calculation methods
  const calculationMethods = useMemo((): CalculationMethod[] => {
    if (!accountData || Array.isArray(accountData) || !dailyGain || !tradeHistory) {
      return [];
    }

    const currentBalance = accountData.balance;
    const currentProfit = accountData.profit;
    const targetProfit = currentBalance; // 100% means doubling the balance
    const profitNeeded = targetProfit - currentProfit;

    const methods: CalculationMethod[] = [];

    // Method 1: Simple Monthly Compound Growth
    if (accountData.monthly > 0) {
      const monthlyRate = accountData.monthly / 100;
      const currentMultiplier = 1 + accountData.absGain / 100;
      const multiplierNeededToDouble = 2 / currentMultiplier;
      const monthsToDouble = Math.log(multiplierNeededToDouble) / Math.log(1 + monthlyRate);
      const daysToDouble = Math.ceil(monthsToDouble * 30.44);

      methods.push({
        name: "Monthly Compound Growth",
        icon: <TrendingUp className="w-4 h-4" />,
        description: "Based on historical monthly growth rate with compound interest",
        daysToDouble: daysToDouble > 0 ? daysToDouble : null,
        confidence: 75,
        details: {
          assumptions: [
            `Monthly growth rate remains constant at ${accountData.monthly.toFixed(2)}%`,
            "Compound growth continues at same pace",
            "No major market disruptions"
          ],
          calculations: [
            `Current balance: ${formatCurrency(currentBalance)}`,
            `Current total profit: ${formatCurrency(currentProfit)}`,
            `Target profit (100%): ${formatCurrency(targetProfit)}`,
            `Profit needed: ${formatCurrency(profitNeeded)}`,
            `Current multiplier: ${currentMultiplier.toFixed(4)}`,
            `Multiplier needed to double: ${multiplierNeededToDouble.toFixed(4)}`,
            `Months to double: ${monthsToDouble.toFixed(2)}`,
            `Days to double: ${daysToDouble}`
          ],
          factors: [
            "Historical monthly performance",
            "Compound interest effect",
            "Current profit position"
          ],
          limitations: [
            "Assumes consistent monthly performance",
            "Doesn't account for lot size increases",
            "Market conditions may change"
          ]
        }
      });
    }

    // Method 2: Average Daily Profit
    if (dailyGain.length > 0) {
      const totalDailyProfit = dailyGain.reduce((sum, day) => sum + day.profit, 0);
      const avgDailyProfit = totalDailyProfit / dailyGain.length;
      const tradingDaysInPeriod = dailyGain.length;
      
      if (avgDailyProfit > 0) {
        const daysToDouble = Math.ceil(profitNeeded / avgDailyProfit);
        
        methods.push({
          name: "Average Daily Profit",
          icon: <BarChart3 className="w-4 h-4" />,
          description: "Linear projection based on average daily profit",
          daysToDouble: daysToDouble > 0 ? daysToDouble : null,
          confidence: 60,
          details: {
            assumptions: [
              "Average daily profit remains constant",
              "Linear growth (no compounding)",
              "Trading frequency stays the same"
            ],
            calculations: [
              `Total daily profit data points: ${dailyGain.length}`,
              `Total profit from daily data: ${formatCurrency(totalDailyProfit)}`,
              `Average daily profit: ${formatCurrency(avgDailyProfit)}`,
              `Profit needed: ${formatCurrency(profitNeeded)}`,
              `Days to reach target: ${daysToDouble}`
            ],
            factors: [
              "Historical daily performance",
              "Trading consistency",
              "Market participation rate"
            ],
            limitations: [
              "Doesn't account for compounding",
              "Assumes linear growth",
              "Ignores lot size scaling"
            ]
          }
        });
      }
    }

    // Method 3: Compounding Lot Size Method
    if (tradeHistory.length > 0 && accountData.deposits) {
      // Fixed lot size calculation: lot_size = deposits / 3000 * 0.01
      const currentLotSize = (accountData.deposits / 3000) * 0.01;
      const lotIncreaseThreshold = 3000; // Every $3k deposit increase
      const baseLotSize = 0.01; // Base lot per $3k
      
      // Calculate average profit per lot from trade history
      const totalTradeProfit = tradeHistory.reduce((sum, trade) => sum + trade.profit, 0);
      const avgProfitPerTrade = totalTradeProfit / tradeHistory.length;
      
      // Estimate trades per day (simplified)
      const tradingDays = Math.max(1, Math.ceil(dailyGain.length * 0.8)); // Assume 80% of days are trading days
      const avgTradesPerDay = tradeHistory.length / tradingDays;
      
      // Simulate compounding lot size growth
      let simulatedDeposits = accountData.deposits;
      let simulatedProfit = currentProfit;
      let simulatedLotSize = currentLotSize;
      let days = 0;
      
      while (simulatedProfit < targetProfit && days < 1000) { // Safety limit
        days++;
        
        // Calculate daily profit based on current lot size
        const lotMultiplier = simulatedLotSize / baseLotSize;
        const dailyProfit = (avgProfitPerTrade * avgTradesPerDay * lotMultiplier);
        
        simulatedProfit += dailyProfit;
        
        // Assume new deposits are added periodically to increase lot size
        // For simplification, assume deposits increase proportionally with profit
        const newDeposits = simulatedDeposits + (dailyProfit * 0.1); // 10% of profit goes to increasing deposits
        simulatedDeposits = newDeposits;
        
        // Update lot size based on new deposit level
        simulatedLotSize = (simulatedDeposits / 3000) * 0.01;
      }

      methods.push({
        name: "Compounding Lot Size",
        icon: <Zap className="w-4 h-4" />,
        description: "Accounts for increasing lot sizes based on deposit levels",
        daysToDouble: days < 1000 ? days : null,
        confidence: 85,
        details: {
          assumptions: [
            "Lot size = (deposits / $3000) × 0.01",
            "Trading frequency remains constant",
            "Average profit per trade scales with lot size",
            "Deposits increase with profits"
          ],
          calculations: [
            `Current deposits: ${formatCurrency(accountData.deposits)}`,
            `Current lot size: ${currentLotSize.toFixed(3)} (should be ~0.1)`,
            `Base lot per $3k: ${baseLotSize}`,
            `Average profit per trade: ${formatCurrency(avgProfitPerTrade)}`,
            `Estimated trades per day: ${avgTradesPerDay.toFixed(2)}`,
            `Days to double with compounding: ${days}`
          ],
          factors: [
            "Deposit-based lot size scaling",
            "Trade frequency consistency", 
            "Profit acceleration from larger positions"
          ],
          limitations: [
            "Assumes deposits increase with profits",
            "Doesn't account for increased risk",
            "Market conditions may limit large positions"
          ]
        }
      });
    }

    // Method 4: Linear Regression Trend
    if (dataDaily && !dataDaily.error && dataDaily.dataDaily.length > 30) {
      const balanceData = dataDaily.dataDaily.map((d, i) => ({ x: i, y: d.balance }));
      
      // Simple linear regression
      const n = balanceData.length;
      const sumX = balanceData.reduce((sum, d) => sum + d.x, 0);
      const sumY = balanceData.reduce((sum, d) => sum + d.y, 0);
      const sumXY = balanceData.reduce((sum, d) => sum + d.x * d.y, 0);
      const sumX2 = balanceData.reduce((sum, d) => sum + d.x * d.x, 0);
      
      const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
      const intercept = (sumY - slope * sumX) / n;
      
      if (slope > 0) {
        const currentDay = n;
        const targetBalance = currentBalance * 2; // Double the current balance
        const daysToTarget = Math.ceil((targetBalance - intercept) / slope - currentDay);
        
        methods.push({
          name: "Linear Regression Trend",
          icon: <Brain className="w-4 h-4" />,
          description: "Statistical trend analysis of balance growth",
          daysToDouble: daysToTarget > 0 ? daysToTarget : null,
          confidence: 65,
          details: {
            assumptions: [
              "Balance growth follows linear trend",
              "Historical trend continues unchanged",
              "No significant market regime changes"
            ],
            calculations: [
              `Data points analyzed: ${n}`,
              `Linear regression slope: ${slope.toFixed(6)}`,
              `Y-intercept: ${formatCurrency(intercept)}`,
              `Current balance: ${formatCurrency(currentBalance)}`,
              `Target balance: ${formatCurrency(targetBalance)}`,
              `Days to reach target: ${daysToTarget}`
            ],
            factors: [
              "Historical balance progression",
              "Statistical trend analysis",
              "Long-term growth pattern"
            ],
            limitations: [
              "Assumes linear growth (may not be realistic)",
              "Sensitive to outliers",
              "Doesn't account for changing market conditions"
            ]
          }
        });
      }
    }

    return methods.filter(m => m.daysToDouble !== null).sort((a, b) => (a.daysToDouble || 0) - (b.daysToDouble || 0));
  }, [accountData, dailyGain, tradeHistory, dataDaily]);

  const generatePredictionData = (months: number) => {
    if (!accountData || Array.isArray(accountData) || weeklyData.length === 0) {
      return [];
    }

    const monthlyRate = accountData.monthly / 100;
    const data = [];
    const lastWeek = weeklyData[weeklyData.length - 1];
    let cumulativeProfit = accountData.profit;

    for (let i = 1; i <= months * 4; i++) {
      const date = new Date(lastWeek.endDate);
      date.setDate(date.getDate() + i * 7);

      const monthsFraction = i / 4;
      const growthFactor = Math.pow(1 + monthlyRate, monthsFraction);
      const projectedProfit = cumulativeProfit * growthFactor;

      data.push({
        date: date.toLocaleString("default", {
          month: "short",
          day: "numeric",
        }),
        profit: Math.round(projectedProfit),
        optimistic: Math.round(projectedProfit * 1.2),
        conservative: Math.round(projectedProfit * 0.8),
      });
    }
    return data;
  };

  const data = generatePredictionData(timeframe);
  
  // Get monthly compound growth method for header
  const monthlyMethod = calculationMethods.find(m => m.name === "Monthly Compound Growth");
  
  // Calculate consensus as summation of all methods
  const consensusDays = calculationMethods.length > 0 
    ? calculationMethods.reduce((sum, m) => sum + (m.daysToDouble || 0), 0)
    : null;

  if (isDailyGainLoading || isAccountLoading || isTradeHistoryLoading || isDataDailyLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-1/2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="flex items-center gap-2">
            Profit Prediction
            {monthlyMethod && (
              <span className="text-sm text-muted-foreground font-normal">
                (Est. 100% profit in {monthlyMethod.daysToDouble}d)
              </span>
            )}
          </CardTitle>
        </div>
        <div className="flex gap-2">
          <Dialog open={showCalculations} onOpenChange={setShowCalculations}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <Calculator className="w-4 h-4 mr-2" />
                View Calculations
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[80vh]">
              <DialogHeader>
                <DialogTitle>Profit Doubling Calculations</DialogTitle>
                <DialogDescription>
                  Multiple methods for calculating when the account will reach 100% profitability
                </DialogDescription>
              </DialogHeader>
              <ScrollArea className="h-[60vh]">
                <Tabs defaultValue="overview" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="details">Detailed Methods</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="overview" className="space-y-4">
                    <div className="grid gap-4">
                      <h3 className="text-lg font-semibold">Summary of All Methods</h3>
                      <div className="grid gap-3">
                        {calculationMethods.map((method, index) => (
                          <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                            <div className="flex items-center gap-3">
                              {method.icon}
                              <div>
                                <div className="font-medium">{method.name}</div>
                                <div className="text-sm text-muted-foreground">{method.description}</div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-bold">{method.daysToDouble} days</div>
                              <Badge variant={method.confidence >= 80 ? "default" : method.confidence >= 70 ? "secondary" : "outline"}>
                                {method.confidence}% confidence
                              </Badge>
                            </div>
                          </div>
                        ))}
                      </div>
                      {/* {consensusDays && ( */}
                        {/* <div className="p-4 bg-muted rounded-lg"> */}
                          {/* <div className="font-semibold">Consensus Estimate (Summation)</div> */}
                          {/* <div className="text-2xl font-bold text-primary">{consensusDays} days</div> */}
                          {/* <div className="text-sm text-muted-foreground"> */}
                            {/* Sum of all {calculationMethods.length} method estimates */}
                          {/* </div> */}
                        {/* </div> */}
                      {/* )} */}
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="details" className="space-y-6">
                    {calculationMethods.map((method, index) => (
                      <div key={index} className="border rounded-lg p-4 space-y-4">
                        <div className="flex items-center gap-2">
                          {method.icon}
                          <h3 className="text-lg font-semibold">{method.name}</h3>
                          <Badge variant={method.confidence >= 80 ? "default" : method.confidence >= 70 ? "secondary" : "outline"}>
                            {method.confidence}% confidence
                          </Badge>
                        </div>
                        
                        <p className="text-muted-foreground">{method.description}</p>
                        
                        <div className="text-2xl font-bold text-primary">
                          {method.daysToDouble} days to double
                        </div>

                        <div className="grid md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-semibold text-sm mb-2">Assumptions</h4>
                            <ul className="text-sm space-y-1">
                              {method.details.assumptions.map((assumption, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-muted-foreground">•</span>
                                  <span>{assumption}</span>
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div>
                            <h4 className="font-semibold text-sm mb-2">Key Factors</h4>
                            <ul className="text-sm space-y-1">
                              {method.details.factors.map((factor, i) => (
                                <li key={i} className="flex items-start gap-2">
                                  <span className="text-muted-foreground">•</span>
                                  <span>{factor}</span>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        <div>
                          <h4 className="font-semibold text-sm mb-2">Calculations</h4>
                          <div className="bg-muted p-3 rounded font-mono text-sm space-y-1">
                            {method.details.calculations.map((calc, i) => (
                              <div key={i}>{calc}</div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 className="font-semibold text-sm mb-2">Limitations</h4>
                          <ul className="text-sm space-y-1 text-muted-foreground">
                            {method.details.limitations.map((limitation, i) => (
                              <li key={i} className="flex items-start gap-2">
                                <span>⚠</span>
                                <span>{limitation}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    ))}
                  </TabsContent>
                </Tabs>
              </ScrollArea>
            </DialogContent>
          </Dialog>
          <Button
            variant={timeframe === 6 ? "default" : "outline"}
            onClick={() => setTimeframe(6)}
          >
            6M
          </Button>
          <Button
            variant={timeframe === 12 ? "default" : "outline"}
            onClick={() => setTimeframe(12)}
          >
            12M
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ChartContainer config={{}} className="h-[300px] w-full">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="date"
              stroke="hsl(var(--foreground))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <YAxis
              tickFormatter={formatCurrency}
              stroke="hsl(var(--foreground))"
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <Tooltip
              formatter={formatCurrency}
              contentStyle={{
                backgroundColor: "hsl(var(--background))",
                border: "1px solid hsl(var(--border))",
                color: "hsl(var(--foreground))",
              }}
            />
            <Legend
              wrapperStyle={{
                color: "hsl(var(--foreground))",
              }}
            />
            <Line
              type="monotone"
              dataKey="profit"
              name="Projected Profit"
              stroke="hsl(var(--primary))"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
            />
            <Line
              type="monotone"
              dataKey="optimistic"
              name="Optimistic"
              stroke="hsl(47 100% 50%)"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
            />
            <Line
              type="monotone"
              dataKey="conservative"
              name="Conservative"
              stroke="hsl(var(--muted-foreground))"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ChartContainer>
      </CardContent>
    </Card>
  );
};

export default ProfitPrediction;

