"""
Scenario Comparator

Ranks and compares multiple financing scenarios based on weighted criteria.
Supports custom weighting for different stakeholder priorities.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from enum import Enum

from backend.engines.scenario_optimizer.scenario_evaluator import ScenarioEvaluation

logger = logging.getLogger(__name__)


class RankingCriterion(Enum):
    """Criteria for ranking scenarios."""
    EQUITY_IRR = "equity_irr"
    TAX_INCENTIVES = "tax_incentives"
    PROBABILITY_OF_RECOUPMENT = "probability_of_recoupment"
    COST_OF_CAPITAL = "cost_of_capital"
    OVERALL_SCORE = "overall_score"
    DEBT_RECOVERY = "debt_recovery"


@dataclass
class ScenarioRanking:
    """
    Ranking of a single scenario.

    Attributes:
        rank: Rank position (1 = best)
        scenario_name: Scenario identifier
        evaluation: Full ScenarioEvaluation
        weighted_score: Final weighted score
        criterion_scores: Scores by criterion
        percentile_rank: Percentile ranking (0-100)
    """
    rank: int
    scenario_name: str
    evaluation: ScenarioEvaluation
    weighted_score: Decimal
    criterion_scores: Dict[str, Decimal] = field(default_factory=dict)
    percentile_rank: Decimal = Decimal("0")

    def __str__(self) -> str:
        """String representation."""
        return (f"Rank #{self.rank}: {self.scenario_name} "
                f"(Score: {self.weighted_score:.1f}, "
                f"Equity IRR: {self.evaluation.equity_irr or 0:.1f}%)")


@dataclass
class ComparisonMatrix:
    """
    Head-to-head comparison matrix.

    Attributes:
        scenarios: List of scenario names
        matrix: scenario_a → scenario_b → comparison result
        win_counts: scenario → number of wins
    """
    scenarios: List[str]
    matrix: Dict[str, Dict[str, str]]  # "wins", "loses", "ties"
    win_counts: Dict[str, int]


class ScenarioComparator:
    """
    Compare and rank multiple financing scenarios.

    Supports customizable weighting for different stakeholder priorities
    (e.g., equity investors prioritize IRR, producers prioritize ownership).
    """

    # Default weights for ranking criteria
    DEFAULT_WEIGHTS = {
        RankingCriterion.EQUITY_IRR: Decimal("0.30"),
        RankingCriterion.TAX_INCENTIVES: Decimal("0.15"),
        RankingCriterion.PROBABILITY_OF_RECOUPMENT: Decimal("0.25"),
        RankingCriterion.COST_OF_CAPITAL: Decimal("0.15"),
        RankingCriterion.DEBT_RECOVERY: Decimal("0.15")
    }

    # Pre-defined stakeholder perspectives
    EQUITY_INVESTOR_WEIGHTS = {
        RankingCriterion.EQUITY_IRR: Decimal("0.50"),
        RankingCriterion.PROBABILITY_OF_RECOUPMENT: Decimal("0.30"),
        RankingCriterion.TAX_INCENTIVES: Decimal("0.10"),
        RankingCriterion.COST_OF_CAPITAL: Decimal("0.05"),
        RankingCriterion.DEBT_RECOVERY: Decimal("0.05")
    }

    PRODUCER_WEIGHTS = {
        RankingCriterion.TAX_INCENTIVES: Decimal("0.35"),
        RankingCriterion.COST_OF_CAPITAL: Decimal("0.25"),
        RankingCriterion.EQUITY_IRR: Decimal("0.20"),
        RankingCriterion.PROBABILITY_OF_RECOUPMENT: Decimal("0.15"),
        RankingCriterion.DEBT_RECOVERY: Decimal("0.05")
    }

    LENDER_WEIGHTS = {
        RankingCriterion.DEBT_RECOVERY: Decimal("0.50"),
        RankingCriterion.PROBABILITY_OF_RECOUPMENT: Decimal("0.30"),
        RankingCriterion.COST_OF_CAPITAL: Decimal("0.10"),
        RankingCriterion.TAX_INCENTIVES: Decimal("0.05"),
        RankingCriterion.EQUITY_IRR: Decimal("0.05")
    }

    def __init__(
        self,
        weights: Optional[Dict[RankingCriterion, Decimal]] = None,
        stakeholder_perspective: Optional[str] = None
    ):
        """
        Initialize comparator.

        Args:
            weights: Custom weights for ranking criteria
            stakeholder_perspective: Pre-defined perspective ("equity", "producer", "lender")
        """
        if stakeholder_perspective:
            if stakeholder_perspective.lower() == "equity":
                self.weights = self.EQUITY_INVESTOR_WEIGHTS
            elif stakeholder_perspective.lower() == "producer":
                self.weights = self.PRODUCER_WEIGHTS
            elif stakeholder_perspective.lower() == "lender":
                self.weights = self.LENDER_WEIGHTS
            else:
                logger.warning(f"Unknown perspective '{stakeholder_perspective}', using default")
                self.weights = self.DEFAULT_WEIGHTS
        else:
            self.weights = weights or self.DEFAULT_WEIGHTS

        logger.info(f"ScenarioComparator initialized with weights: {self.weights}")

    def rank_scenarios(
        self,
        evaluations: List[ScenarioEvaluation]
    ) -> List[ScenarioRanking]:
        """
        Rank scenarios by weighted criteria.

        Args:
            evaluations: List of ScenarioEvaluation objects

        Returns:
            List of ScenarioRanking sorted by rank (best first)
        """
        if not evaluations:
            logger.warning("No scenarios to rank")
            return []

        logger.info(f"Ranking {len(evaluations)} scenarios")

        # Calculate weighted scores
        rankings = []
        for evaluation in evaluations:
            criterion_scores = self._calculate_criterion_scores(evaluation)
            weighted_score = self._calculate_weighted_score(criterion_scores)

            ranking = ScenarioRanking(
                rank=0,  # Will be assigned after sorting
                scenario_name=evaluation.scenario_name,
                evaluation=evaluation,
                weighted_score=weighted_score,
                criterion_scores=criterion_scores
            )
            rankings.append(ranking)

        # Sort by weighted score (descending)
        rankings.sort(key=lambda r: r.weighted_score, reverse=True)

        # Assign ranks and percentiles
        for i, ranking in enumerate(rankings):
            ranking.rank = i + 1
            ranking.percentile_rank = (Decimal(str(len(rankings) - i)) / Decimal(str(len(rankings)))) * Decimal("100")

        logger.info(f"Ranking complete. Winner: {rankings[0].scenario_name} ({rankings[0].weighted_score:.1f})")

        return rankings

    def compare_two_scenarios(
        self,
        eval_a: ScenarioEvaluation,
        eval_b: ScenarioEvaluation
    ) -> Tuple[str, Dict[str, str]]:
        """
        Compare two scenarios head-to-head.

        Args:
            eval_a: First scenario evaluation
            eval_b: Second scenario evaluation

        Returns:
            Tuple of (winner_name, criterion_winners_dict)
        """
        criterion_winners = {}
        a_wins = 0
        b_wins = 0

        # Compare on each criterion
        for criterion in self.weights.keys():
            value_a = self._get_criterion_value(eval_a, criterion)
            value_b = self._get_criterion_value(eval_b, criterion)

            # Determine winner (higher is better for all current criteria)
            if value_a > value_b:
                criterion_winners[criterion.value] = eval_a.scenario_name
                a_wins += 1
            elif value_b > value_a:
                criterion_winners[criterion.value] = eval_b.scenario_name
                b_wins += 1
            else:
                criterion_winners[criterion.value] = "tie"

        # Overall winner
        if a_wins > b_wins:
            winner = eval_a.scenario_name
        elif b_wins > a_wins:
            winner = eval_b.scenario_name
        else:
            winner = "tie"

        logger.info(f"Head-to-head: {winner} wins ({eval_a.scenario_name}: {a_wins}, {eval_b.scenario_name}: {b_wins})")

        return winner, criterion_winners

    def generate_comparison_matrix(
        self,
        evaluations: List[ScenarioEvaluation]
    ) -> ComparisonMatrix:
        """
        Generate pairwise comparison matrix.

        Args:
            evaluations: List of evaluations to compare

        Returns:
            ComparisonMatrix with all pairwise comparisons
        """
        scenario_names = [e.scenario_name for e in evaluations]
        matrix: Dict[str, Dict[str, str]] = {name: {} for name in scenario_names}
        win_counts = {name: 0 for name in scenario_names}

        # Pairwise comparisons
        for i, eval_a in enumerate(evaluations):
            for j, eval_b in enumerate(evaluations):
                if i == j:
                    matrix[eval_a.scenario_name][eval_b.scenario_name] = "self"
                    continue

                winner, _ = self.compare_two_scenarios(eval_a, eval_b)

                if winner == eval_a.scenario_name:
                    matrix[eval_a.scenario_name][eval_b.scenario_name] = "wins"
                    win_counts[eval_a.scenario_name] += 1
                elif winner == eval_b.scenario_name:
                    matrix[eval_a.scenario_name][eval_b.scenario_name] = "loses"
                else:
                    matrix[eval_a.scenario_name][eval_b.scenario_name] = "ties"

        comparison_matrix = ComparisonMatrix(
            scenarios=scenario_names,
            matrix=matrix,
            win_counts=win_counts
        )

        logger.info(f"Comparison matrix generated for {len(scenario_names)} scenarios")

        return comparison_matrix

    def get_top_n_scenarios(
        self,
        evaluations: List[ScenarioEvaluation],
        n: int = 3
    ) -> List[ScenarioRanking]:
        """
        Get top N scenarios.

        Args:
            evaluations: List of evaluations
            n: Number of top scenarios to return

        Returns:
            Top N rankings
        """
        rankings = self.rank_scenarios(evaluations)
        return rankings[:min(n, len(rankings))]

    def get_best_by_criterion(
        self,
        evaluations: List[ScenarioEvaluation],
        criterion: RankingCriterion
    ) -> ScenarioEvaluation:
        """
        Get best scenario for a specific criterion.

        Args:
            evaluations: List of evaluations
            criterion: Criterion to optimize

        Returns:
            Best ScenarioEvaluation for that criterion
        """
        if not evaluations:
            raise ValueError("No scenarios to compare")

        best_eval = max(
            evaluations,
            key=lambda e: self._get_criterion_value(e, criterion)
        )

        logger.info(f"Best for {criterion.value}: {best_eval.scenario_name}")

        return best_eval

    def _calculate_criterion_scores(
        self,
        evaluation: ScenarioEvaluation
    ) -> Dict[RankingCriterion, Decimal]:
        """
        Calculate normalized scores (0-100) for each criterion.

        Args:
            evaluation: ScenarioEvaluation to score

        Returns:
            Dict mapping criterion → score
        """
        scores = {}

        # Equity IRR (target 20% = 100 points)
        if evaluation.equity_irr:
            irr_score = min((evaluation.equity_irr / Decimal("20.0")) * Decimal("100"), Decimal("100"))
            scores[RankingCriterion.EQUITY_IRR] = irr_score
        else:
            scores[RankingCriterion.EQUITY_IRR] = Decimal("0")

        # Tax Incentives (target 20% of budget = 100 points)
        incentive_score = min((evaluation.tax_incentive_effective_rate / Decimal("20.0")) * Decimal("100"), Decimal("100"))
        scores[RankingCriterion.TAX_INCENTIVES] = incentive_score

        # Probability of Recoupment (80% = 100 points)
        recoupment_score = min((evaluation.probability_of_equity_recoupment / Decimal("0.80")) * Decimal("100"), Decimal("100"))
        scores[RankingCriterion.PROBABILITY_OF_RECOUPMENT] = recoupment_score

        # Cost of Capital (lower is better, 10% = 100 points, 20% = 0 points)
        if evaluation.weighted_cost_of_capital > 0:
            cost_score = Decimal("100") - ((evaluation.weighted_cost_of_capital - Decimal("10.0")) * Decimal("10"))
            cost_score = max(min(cost_score, Decimal("100")), Decimal("0"))
            scores[RankingCriterion.COST_OF_CAPITAL] = cost_score
        else:
            scores[RankingCriterion.COST_OF_CAPITAL] = Decimal("50")

        # Debt Recovery (100% = 100 points)
        debt_score = min(evaluation.senior_debt_recovery_rate, Decimal("100"))
        scores[RankingCriterion.DEBT_RECOVERY] = debt_score

        # Overall Score (already 0-100)
        scores[RankingCriterion.OVERALL_SCORE] = evaluation.overall_score

        return scores

    def _calculate_weighted_score(
        self,
        criterion_scores: Dict[RankingCriterion, Decimal]
    ) -> Decimal:
        """Calculate final weighted score."""
        weighted_score = Decimal("0")

        for criterion, weight in self.weights.items():
            score = criterion_scores.get(criterion, Decimal("0"))
            weighted_score += score * weight

        return weighted_score

    def _get_criterion_value(
        self,
        evaluation: ScenarioEvaluation,
        criterion: RankingCriterion
    ) -> Decimal:
        """Extract raw criterion value from evaluation."""
        if criterion == RankingCriterion.EQUITY_IRR:
            return evaluation.equity_irr or Decimal("0")
        elif criterion == RankingCriterion.TAX_INCENTIVES:
            return evaluation.tax_incentive_effective_rate
        elif criterion == RankingCriterion.PROBABILITY_OF_RECOUPMENT:
            return evaluation.probability_of_equity_recoupment
        elif criterion == RankingCriterion.COST_OF_CAPITAL:
            # Invert for "lower is better"
            return Decimal("100") - evaluation.weighted_cost_of_capital
        elif criterion == RankingCriterion.DEBT_RECOVERY:
            return evaluation.senior_debt_recovery_rate
        elif criterion == RankingCriterion.OVERALL_SCORE:
            return evaluation.overall_score
        else:
            return Decimal("0")

    def print_ranking_report(self, rankings: List[ScenarioRanking]):
        """Print formatted ranking report."""
        print("\n" + "=" * 80)
        print("SCENARIO RANKING REPORT")
        print("=" * 80)

        for ranking in rankings:
            eval = ranking.evaluation
            print(f"\n#{ranking.rank}: {ranking.scenario_name}")
            print(f"  Weighted Score: {ranking.weighted_score:.1f}/100")
            print(f"  Percentile: {ranking.percentile_rank:.0f}th")
            print(f"\n  Key Metrics:")
            print(f"    Equity IRR: {eval.equity_irr or 0:.1f}%")
            print(f"    Tax Incentives: {eval.tax_incentive_effective_rate:.1f}% of budget")
            print(f"    Probability of Recoupment: {eval.probability_of_equity_recoupment * Decimal('100'):.0f}%")
            print(f"    Cost of Capital: {eval.weighted_cost_of_capital:.1f}%")
            print(f"    Debt Recovery: {eval.senior_debt_recovery_rate:.0f}%")

            if eval.strengths:
                print(f"\n  Strengths:")
                for strength in eval.strengths:
                    print(f"    + {strength}")

            if eval.weaknesses:
                print(f"\n  Weaknesses:")
                for weakness in eval.weaknesses:
                    print(f"    - {weakness}")

        print("\n" + "=" * 80)
