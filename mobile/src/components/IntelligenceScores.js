import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS, BASE } from '../theme';

const LABELS = {
    earnings_stability: 'Earnings Stability', cash_flow_quality: 'Cash Flow Quality',
    balance_sheet: 'Balance Sheet', return_metrics: 'Return Metrics',
    growth_visibility: 'Growth Visibility', model_agreement: 'Model Agreement',
    gross_margin_stability: 'Gross Margin', roic_spread: 'ROIC Spread',
    growth_vs_industry: 'Growth vs Industry', intangible_intensity: 'Intangible Intensity',
    brand_proxy: 'Brand Power', operating_leverage: 'Op. Leverage',
    roe_consistency: 'ROE Consistency', fcf_consistency: 'FCF Consistency',
    debt_levels: 'Debt Levels', margin_expansion: 'Margin Expansion',
    earnings_predictability: 'Earnings Predict.', capex_discipline: 'CapEx Discipline',
    share_dilution: 'Share Dilution',
};

function ScorePanel({ score, max, label, badge, badgeColor, badgeBg, components }) {
    const pct = Math.min(score / max * 100, 100);

    return (
        <View style={s.panel}>
            <View style={s.ringWrap}>
                <View style={[s.ringOuter, { borderColor: COLORS.borderLight }]}>
                    <Text style={s.ringValue}>{score}<Text style={s.ringMax}>/{max}</Text></Text>
                </View>
                <View style={[s.progressBar, { width: `${pct}%`, backgroundColor: badgeColor }]} />
            </View>
            <Text style={s.panelLabel}>{label}</Text>
            {badge && (
                <View style={[s.badge, { backgroundColor: badgeBg }]}>
                    <Text style={[s.badgeText, { color: badgeColor }]}>{badge}</Text>
                </View>
            )}
            {components && (
                <View style={s.breakdown}>
                    {Object.entries(components).map(([key, comp]) => {
                        const barPct = comp.max > 0 ? (comp.score / comp.max * 100) : 0;
                        return (
                            <View key={key} style={s.compRow}>
                                <Text style={s.compName} numberOfLines={1}>{LABELS[key] || key}</Text>
                                <View style={s.compBarWrap}>
                                    <View style={[s.compBar, { width: `${barPct}%` }]} />
                                </View>
                                <Text style={s.compVal}>{comp.score}/{comp.max}</Text>
                            </View>
                        );
                    })}
                </View>
            )}
        </View>
    );
}

export default function IntelligenceScores({ confidence, moat, scores }) {
    const q100 = scores?.quality_score_100;

    const confColor = confidence?.badge === 'High' ? COLORS.greenDeep : confidence?.badge === 'Moderate' ? COLORS.amber : COLORS.redDeep;
    const confBg = confidence?.badge === 'High' ? COLORS.greenBg : confidence?.badge === 'Moderate' ? COLORS.amberBg : COLORS.redBg;

    const moatColor = moat?.classification === 'Wide Moat' ? COLORS.greenDeep : moat?.classification === 'Narrow Moat' ? COLORS.amber : COLORS.redDeep;
    const moatBg = moat?.classification === 'Wide Moat' ? COLORS.greenBg : moat?.classification === 'Narrow Moat' ? COLORS.amberBg : COLORS.redBg;

    const qualColor = q100 >= 70 ? COLORS.greenDeep : q100 >= 45 ? COLORS.amber : COLORS.redDeep;
    const qualBg = q100 >= 70 ? COLORS.greenBg : q100 >= 45 ? COLORS.amberBg : COLORS.redBg;
    const qualBadge = q100 >= 70 ? 'High Quality' : q100 >= 45 ? 'Moderate' : 'Low Quality';

    return (
        <View style={s.section}>
            <Text style={s.sectionTitle}>INTELLIGENCE SCORES</Text>
            <ScorePanel score={confidence?.score ?? 0} max={100} label="Valuation Confidence"
                badge={confidence?.badge} badgeColor={confColor} badgeBg={confBg} components={confidence?.components} />
            <ScorePanel score={moat?.score ?? 0} max={100} label="Competitive Moat"
                badge={moat?.classification} badgeColor={moatColor} badgeBg={moatBg} components={moat?.components} />
            <ScorePanel score={q100 ?? 0} max={100} label="Business Quality"
                badge={qualBadge} badgeColor={qualColor} badgeBg={qualBg} components={scores?.quality_components} />
        </View>
    );
}

const s = StyleSheet.create({
    section: { marginBottom: 16 },
    sectionTitle: { fontSize: 10, fontWeight: '600', color: COLORS.textTertiary, letterSpacing: 1.5, marginBottom: 12 },
    panel: {
        backgroundColor: COLORS.surface,
        borderRadius: BASE.radiusLg,
        padding: 20,
        marginBottom: 12,
        borderWidth: 1,
        borderColor: COLORS.border,
        alignItems: 'center',
    },
    ringWrap: { alignItems: 'center', marginBottom: 12 },
    ringOuter: { width: 90, height: 90, borderRadius: 45, borderWidth: 6, justifyContent: 'center', alignItems: 'center' },
    ringValue: { fontSize: 28, fontWeight: '700', color: COLORS.textPrimary },
    ringMax: { fontSize: 12, color: COLORS.textTertiary, fontWeight: '500' },
    progressBar: { height: 4, borderRadius: 2, marginTop: 8, alignSelf: 'stretch' },
    panelLabel: { fontSize: 14, fontWeight: '600', color: COLORS.textPrimary, marginBottom: 6 },
    badge: { paddingHorizontal: 12, paddingVertical: 3, borderRadius: 100, marginBottom: 8 },
    badgeText: { fontSize: 11, fontWeight: '600' },
    breakdown: { alignSelf: 'stretch', paddingTop: 12, borderTopWidth: 1, borderTopColor: COLORS.borderLight },
    compRow: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 3 },
    compName: { fontSize: 11, color: COLORS.textSecondary, flex: 1 },
    compBarWrap: { width: 60, height: 4, backgroundColor: COLORS.borderLight, borderRadius: 2, overflow: 'hidden' },
    compBar: { height: '100%', backgroundColor: COLORS.blue, borderRadius: 2 },
    compVal: { fontSize: 11, fontWeight: '600', color: COLORS.textPrimary, width: 40, textAlign: 'right' },
});
