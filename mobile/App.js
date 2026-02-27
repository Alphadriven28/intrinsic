import React, { useState } from 'react';
import {
  StyleSheet, View, Text, TextInput, TouchableOpacity,
  ScrollView, ActivityIndicator, SafeAreaView, StatusBar, KeyboardAvoidingView, Platform
} from 'react-native';
import { COLORS, BASE } from './src/theme';
import { analyzeStock } from './src/services/api';
import CompanyHeader from './src/components/CompanyHeader';
import MasterValuationCard from './src/components/MasterValuationCard';
import ModelGrid from './src/components/ModelGrid';
import IntelligenceScores from './src/components/IntelligenceScores';
import WeightChart from './src/components/WeightChart';
import RiskSection from './src/components/RiskSection';
import ExecutiveSummary from './src/components/ExecutiveSummary';

export default function App() {
  const [ticker, setTicker] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async () => {
    if (!ticker.trim()) return;
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const result = await analyzeStock(ticker);
      setData(result);
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={s.safe}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView style={s.scroll} contentContainerStyle={s.scrollContent} keyboardShouldPersistTaps="handled">
          {/* Header */}
          <View style={s.header}>
            <Text style={s.brand}>INTRINSIC</Text>
            <Text style={s.tagline}>Institutional Equity Research & Valuation Intelligence</Text>
          </View>

          {/* Search */}
          <View style={s.searchRow}>
            <TextInput
              style={s.searchInput}
              placeholder="Enter ticker (e.g. AAPL)"
              placeholderTextColor={COLORS.textTertiary}
              value={ticker}
              onChangeText={setTicker}
              autoCapitalize="characters"
              autoCorrect={false}
              returnKeyType="search"
              onSubmitEditing={handleSearch}
              editable={!loading}
            />
            <TouchableOpacity
              style={[s.searchBtn, loading && s.searchBtnDisabled]}
              onPress={handleSearch}
              disabled={loading}
              activeOpacity={0.7}
            >
              <Text style={s.searchBtnText}>Analyze</Text>
            </TouchableOpacity>
          </View>

          {/* Loading */}
          {loading && (
            <View style={s.loadingWrap}>
              <ActivityIndicator size="large" color={COLORS.textPrimary} />
              <Text style={s.loadingText}>Analyzing {ticker.toUpperCase()}...</Text>
              <Text style={s.loadingSubtext}>Running 9 valuation models</Text>
            </View>
          )}

          {/* Error */}
          {error && (
            <View style={s.errorWrap}>
              <Text style={s.errorIcon}>⚠️</Text>
              <Text style={s.errorText}>{error}</Text>
            </View>
          )}

          {/* Results */}
          {data && !loading && (
            <View>
              <CompanyHeader company={data.company} valuation={data.valuation} weighting={data.weighting} />
              <MasterValuationCard valuation={data.valuation} weighting={data.weighting} master={data.master} />
              <ModelGrid models={data.valuation?.models} weighting={data.weighting} currentPrice={data.company?.price} />
              <IntelligenceScores confidence={data.confidence} moat={data.moat} scores={data.scores} />
              <WeightChart weighting={data.weighting} />
              <RiskSection risk={data.risk} />
              <ExecutiveSummary summary={data.summary} />
            </View>
          )}

          {/* Footer */}
          <View style={s.footer}>
            <Text style={s.footerText}>Intrinsic — Quantitative equity research intelligence.</Text>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: COLORS.bg },
  scroll: { flex: 1 },
  scrollContent: { padding: 20, paddingBottom: 40 },
  header: { alignItems: 'center', paddingTop: 40, paddingBottom: 30 },
  brand: { fontSize: 12, fontWeight: '600', letterSpacing: 3, color: COLORS.textTertiary, marginBottom: 6 },
  tagline: { fontSize: 14, color: COLORS.textSecondary, textAlign: 'center' },
  searchRow: { flexDirection: 'row', gap: 8, marginBottom: 24 },
  searchInput: {
    flex: 1,
    backgroundColor: COLORS.surface,
    borderWidth: 1.5,
    borderColor: COLORS.border,
    borderRadius: BASE.radiusMd,
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 15,
    fontWeight: '500',
    color: COLORS.textPrimary,
    letterSpacing: 0.5,
  },
  searchBtn: {
    backgroundColor: COLORS.textPrimary,
    borderRadius: BASE.radiusMd,
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  searchBtnDisabled: { backgroundColor: COLORS.textTertiary },
  searchBtnText: { color: '#fff', fontSize: 14, fontWeight: '500' },
  loadingWrap: { alignItems: 'center', paddingVertical: 60 },
  loadingText: { fontSize: 14, color: COLORS.textTertiary, marginTop: 16 },
  loadingSubtext: { fontSize: 12, color: COLORS.textTertiary, marginTop: 4 },
  errorWrap: { alignItems: 'center', paddingVertical: 30 },
  errorIcon: { fontSize: 24, marginBottom: 8 },
  errorText: { fontSize: 14, color: COLORS.red, textAlign: 'center' },
  footer: { alignItems: 'center', paddingTop: 30, borderTopWidth: 1, borderTopColor: COLORS.borderLight, marginTop: 10 },
  footerText: { fontSize: 11, color: COLORS.textTertiary },
});
