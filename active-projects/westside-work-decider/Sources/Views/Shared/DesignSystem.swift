import SwiftUI

// MARK: - Design System 2025
// A distinctive design system with editorial typography and warm luxury tones
// Aesthetic Direction: Refined luxury meets editorial clarity

// MARK: - Color Palette

enum DS {
    // MARK: Base Colors
    enum Colors {
        // Dark mode base - warm undertone (not cold black)
        static let backgroundPrimary = Color(hex: "09090B")
        static let backgroundSecondary = Color(hex: "121214")
        static let backgroundTertiary = Color(hex: "1A1A1F")
        static let backgroundElevated = Color(hex: "232328")

        // Accent colors - warm luxury palette
        static let accentGold = Color(hex: "D4A853")      // Elite: warm gold (luxury)
        static let accentAmber = Color(hex: "E8B866")     // Elite highlight
        static let accentSlate = Color(hex: "64748B")     // Reliable: sophisticated slate
        static let accentBlue = Color(hex: "5B8DEF")      // Reliable highlight
        static let accentTeal = Color(hex: "2DD4BF")      // Fresh accent
        static let accentPurple = Color(hex: "A78BFA")    // Rare accent only

        // Semantic colors
        static let success = Color(hex: "34D399")
        static let warning = Color(hex: "FBBF24")
        static let error = Color(hex: "F87171")

        // Text colors - warm whites
        static let textPrimary = Color(hex: "FAFAF9")
        static let textSecondary = Color(hex: "A8A29E")
        static let textTertiary = Color(hex: "78716C")
        static let textMuted = Color(hex: "57534E")

        // Tier colors - distinctive luxury hierarchy
        static let elitePrimary = Color(hex: "D4A853")    // Warm gold
        static let eliteGlow = Color(hex: "D4A853").opacity(0.35)
        static let reliablePrimary = Color(hex: "64748B") // Sophisticated slate
        static let reliableGlow = Color(hex: "5B8DEF").opacity(0.25)
        static let unknownPrimary = Color(hex: "525252")

        // Glass effect colors - warmer tint
        static let glassBackground = Color(hex: "FAFAF9").opacity(0.04)
        static let glassBorder = Color(hex: "FAFAF9").opacity(0.08)
        static let glassHighlight = Color(hex: "FAFAF9").opacity(0.12)
    }

    // MARK: Gradients
    enum Gradients {
        // Atmospheric background - warm undertone
        static let meshBackground = RadialGradient(
            colors: [
                Colors.accentGold.opacity(0.04),
                Colors.backgroundPrimary,
                Colors.accentSlate.opacity(0.03),
                Colors.backgroundPrimary
            ],
            center: .topLeading,
            startRadius: 0,
            endRadius: 600
        )

        // Elite: warm gold luxury gradient
        static let eliteCard = LinearGradient(
            colors: [
                Colors.accentGold.opacity(0.12),
                Colors.accentAmber.opacity(0.04)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )

        // Reliable: sophisticated slate gradient
        static let reliableCard = LinearGradient(
            colors: [
                Colors.accentSlate.opacity(0.10),
                Colors.accentBlue.opacity(0.03)
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )

        // Hero: warm gold to slate (luxury editorial)
        static let heroGradient = LinearGradient(
            colors: [
                Colors.accentGold,
                Colors.accentSlate
            ],
            startPoint: .topLeading,
            endPoint: .bottomTrailing
        )

        // Shimmer with warm tone
        static let shimmer = LinearGradient(
            colors: [
                Colors.textPrimary.opacity(0),
                Colors.textPrimary.opacity(0.15),
                Colors.textPrimary.opacity(0)
            ],
            startPoint: .leading,
            endPoint: .trailing
        )
    }

    // MARK: Spacing
    enum Spacing {
        static let xxxs: CGFloat = 2
        static let xxs: CGFloat = 4
        static let xs: CGFloat = 8
        static let sm: CGFloat = 12
        static let md: CGFloat = 16
        static let lg: CGFloat = 20
        static let xl: CGFloat = 24
        static let xxl: CGFloat = 32
        static let xxxl: CGFloat = 40
        static let huge: CGFloat = 56
    }

    // MARK: Corner Radius
    enum Radius {
        static let xs: CGFloat = 8
        static let sm: CGFloat = 12
        static let md: CGFloat = 16
        static let lg: CGFloat = 20
        static let xl: CGFloat = 24
        static let xxl: CGFloat = 32
        static let full: CGFloat = 9999
    }

    // MARK: Typography
    // Editorial approach: Serif for display, refined sans for body
    enum Typography {
        // Hero: Editorial serif for maximum distinction
        static func hero(_ text: Text) -> some View {
            text
                .font(.system(size: 38, weight: .bold, design: .serif))
                .tracking(-1.5)
        }

        // Title: Serif for editorial hierarchy
        static func title(_ text: Text) -> some View {
            text
                .font(.system(size: 26, weight: .bold, design: .serif))
                .tracking(-0.8)
        }

        // Headline: Clean sans with tight tracking
        static func headline(_ text: Text) -> some View {
            text
                .font(.system(size: 19, weight: .semibold, design: .default))
                .tracking(-0.3)
        }

        // Body: Rounded for warmth and approachability
        static func bodyRounded(_ text: Text) -> some View {
            text
                .font(.system(size: 16, weight: .regular, design: .rounded))
                .tracking(0.1)
        }

        // Caption: Refined, slightly condensed feel
        static func caption(_ text: Text) -> some View {
            text
                .font(.system(size: 13, weight: .medium, design: .default))
                .tracking(0.2)
        }

        // Micro: All-caps with generous tracking
        static func micro(_ text: Text) -> some View {
            text
                .font(.system(size: 10, weight: .bold, design: .default))
                .textCase(.uppercase)
                .tracking(1.2)
        }

        // Display: Large serif for splash moments
        static func display(_ text: Text) -> some View {
            text
                .font(.system(size: 48, weight: .bold, design: .serif))
                .tracking(-2)
        }

        // Label: Compact utility text
        static func label(_ text: Text) -> some View {
            text
                .font(.system(size: 12, weight: .semibold, design: .rounded))
                .tracking(0.3)
        }
    }

    // MARK: Shadows
    enum Shadows {
        static func soft(color: Color = .black) -> some View {
            EmptyView()
                .shadow(color: color.opacity(0.1), radius: 8, x: 0, y: 4)
                .shadow(color: color.opacity(0.05), radius: 2, x: 0, y: 1)
        }

        static func elevated(color: Color = .black) -> some View {
            EmptyView()
                .shadow(color: color.opacity(0.15), radius: 20, x: 0, y: 10)
                .shadow(color: color.opacity(0.1), radius: 8, x: 0, y: 4)
        }

        static func glow(color: Color) -> some View {
            EmptyView()
                .shadow(color: color.opacity(0.5), radius: 20, x: 0, y: 0)
                .shadow(color: color.opacity(0.3), radius: 40, x: 0, y: 0)
        }
    }

    // MARK: Animation
    enum Animation {
        static let springy = SwiftUI.Animation.spring(response: 0.5, dampingFraction: 0.7)
        static let snappy = SwiftUI.Animation.spring(response: 0.35, dampingFraction: 0.8)
        static let smooth = SwiftUI.Animation.easeInOut(duration: 0.3)
        static let quick = SwiftUI.Animation.easeOut(duration: 0.2)
        static let slow = SwiftUI.Animation.easeInOut(duration: 0.5)
    }
}

// MARK: - Color Extension

extension Color {
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }
        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue: Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - View Modifiers

struct GlassCardModifier: ViewModifier {
    let cornerRadius: CGFloat
    let tier: Tier?

    init(cornerRadius: CGFloat = DS.Radius.lg, tier: Tier? = nil) {
        self.cornerRadius = cornerRadius
        self.tier = tier
    }

    func body(content: Content) -> some View {
        content
            .background(
                ZStack {
                    // Base glass
                    RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                        .fill(.ultraThinMaterial)

                    // Tier-based gradient overlay
                    if let tier {
                        RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                            .fill(gradientForTier(tier))
                    }

                    // Top highlight
                    RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                        .fill(
                            LinearGradient(
                                colors: [
                                    Color.white.opacity(0.1),
                                    Color.white.opacity(0)
                                ],
                                startPoint: .top,
                                endPoint: .center
                            )
                        )
                }
            )
            .overlay(
                RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
                    .stroke(
                        LinearGradient(
                            colors: [
                                Color.white.opacity(0.2),
                                Color.white.opacity(0.05)
                            ],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        ),
                        lineWidth: 0.5
                    )
            )
            .shadow(color: tierShadowColor.opacity(0.3), radius: 20, x: 0, y: 10)
            .shadow(color: .black.opacity(0.2), radius: 8, x: 0, y: 4)
    }

    private func gradientForTier(_ tier: Tier) -> LinearGradient {
        switch tier {
        case .elite:
            return DS.Gradients.eliteCard
        case .reliable:
            return DS.Gradients.reliableCard
        case .unknown:
            return LinearGradient(colors: [.clear], startPoint: .top, endPoint: .bottom)
        }
    }

    private var tierShadowColor: Color {
        guard let tier else { return .black }
        switch tier {
        case .elite: return DS.Colors.accentGold
        case .reliable: return DS.Colors.accentSlate
        case .unknown: return .black
        }
    }
}

struct PressableButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.96 : 1)
            .opacity(configuration.isPressed ? 0.9 : 1)
            .animation(DS.Animation.quick, value: configuration.isPressed)
    }
}

struct ShimmerModifier: ViewModifier {
    @State private var phase: CGFloat = 0

    func body(content: Content) -> some View {
        content
            .overlay(
                GeometryReader { geometry in
                    DS.Gradients.shimmer
                        .frame(width: geometry.size.width * 2)
                        .offset(x: phase * geometry.size.width * 2 - geometry.size.width)
                }
                .mask(content)
            )
            .onAppear {
                withAnimation(.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    phase = 1
                }
            }
    }
}

struct HoverCardModifier: ViewModifier {
    @State private var isHovered = false

    func body(content: Content) -> some View {
        content
            .scaleEffect(isHovered ? 1.02 : 1)
            .shadow(
                color: .black.opacity(isHovered ? 0.2 : 0.1),
                radius: isHovered ? 20 : 8,
                x: 0,
                y: isHovered ? 10 : 4
            )
            .animation(DS.Animation.springy, value: isHovered)
            .onHover { hovering in
                isHovered = hovering
            }
    }
}

// MARK: - View Extensions

extension View {
    func glassCard(cornerRadius: CGFloat = DS.Radius.lg, tier: Tier? = nil) -> some View {
        modifier(GlassCardModifier(cornerRadius: cornerRadius, tier: tier))
    }

    func shimmerEffect() -> some View {
        modifier(ShimmerModifier())
    }

    func hoverCard() -> some View {
        modifier(HoverCardModifier())
    }

    func pressableButton() -> some View {
        buttonStyle(PressableButtonStyle())
    }
}

// MARK: - Skeleton Loading Views

struct SkeletonRectangle: View {
    let width: CGFloat?
    let height: CGFloat
    let cornerRadius: CGFloat

    init(width: CGFloat? = nil, height: CGFloat = 16, cornerRadius: CGFloat = DS.Radius.xs) {
        self.width = width
        self.height = height
        self.cornerRadius = cornerRadius
    }

    var body: some View {
        RoundedRectangle(cornerRadius: cornerRadius, style: .continuous)
            .fill(DS.Colors.glassBackground)
            .frame(width: width, height: height)
            .shimmerEffect()
    }
}

struct SpotCardSkeleton: View {
    var body: some View {
        VStack(alignment: .leading, spacing: DS.Spacing.sm) {
            // Header
            HStack {
                SkeletonRectangle(width: 200, height: 20)
                Spacer()
                SkeletonRectangle(width: 60, height: 28, cornerRadius: DS.Radius.full)
            }

            // Subtitle
            HStack(spacing: DS.Spacing.xs) {
                SkeletonRectangle(width: 100, height: 14)
                SkeletonRectangle(width: 80, height: 14)
            }

            // Status
            HStack(spacing: DS.Spacing.sm) {
                SkeletonRectangle(width: 60, height: 24, cornerRadius: DS.Radius.full)
                SkeletonRectangle(width: 100, height: 24, cornerRadius: DS.Radius.full)
            }

            // Notes
            VStack(alignment: .leading, spacing: DS.Spacing.xxs) {
                SkeletonRectangle(height: 12)
                SkeletonRectangle(width: 250, height: 12)
            }

            // Tags
            HStack(spacing: DS.Spacing.xs) {
                ForEach(0..<4, id: \.self) { _ in
                    SkeletonRectangle(width: 70, height: 28, cornerRadius: DS.Radius.full)
                }
            }
        }
        .padding(DS.Spacing.md)
        .glassCard()
    }
}

// MARK: - Haptic Feedback

enum HapticFeedback {
    static func light() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
    }

    static func medium() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
    }

    static func heavy() {
        let generator = UIImpactFeedbackGenerator(style: .heavy)
        generator.impactOccurred()
    }

    static func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }

    static func success() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
    }

    static func error() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.error)
    }
}

// MARK: - Grain Texture Overlay
// Adds subtle film grain for atmospheric depth

struct GrainOverlay: View {
    let opacity: Double

    init(opacity: Double = 0.03) {
        self.opacity = opacity
    }

    var body: some View {
        GeometryReader { geometry in
            Canvas { context, size in
                // Generate deterministic grain pattern
                for x in stride(from: 0, to: size.width, by: 2) {
                    for y in stride(from: 0, to: size.height, by: 2) {
                        let noise = sin(x * 0.1) * cos(y * 0.1) * sin((x + y) * 0.05)
                        let brightness = (noise + 1) / 2
                        context.opacity = brightness * opacity
                        context.fill(
                            Path(CGRect(x: x, y: y, width: 2, height: 2)),
                            with: .color(.white)
                        )
                    }
                }
            }
        }
        .allowsHitTesting(false)
    }
}

struct GrainModifier: ViewModifier {
    let opacity: Double

    func body(content: Content) -> some View {
        content.overlay(GrainOverlay(opacity: opacity))
    }
}

extension View {
    func grainTexture(opacity: Double = 0.03) -> some View {
        modifier(GrainModifier(opacity: opacity))
    }
}

// MARK: - Animated Symbol

struct AnimatedSymbol: View {
    let systemName: String
    let animation: SymbolAnimation
    @State private var trigger = false

    enum SymbolAnimation {
        case bounce
        case pulse
        case scale
    }

    var body: some View {
        Image(systemName: systemName)
            .symbolEffect(.bounce, value: trigger && animation == .bounce)
            .symbolEffect(.pulse, isActive: animation == .pulse)
            .scaleEffect(animation == .scale && trigger ? 1.2 : 1)
            .animation(DS.Animation.springy, value: trigger)
            .onAppear {
                if animation == .bounce || animation == .scale {
                    trigger = true
                }
            }
    }
}

// MARK: - Previews

#Preview("Design System") {
    ScrollView {
        VStack(spacing: DS.Spacing.xl) {
            // Typography showcase
            VStack(alignment: .leading, spacing: DS.Spacing.md) {
                DS.Typography.hero(Text("Hero Title"))
                    .foregroundStyle(DS.Colors.textPrimary)

                DS.Typography.title(Text("Section Title"))
                    .foregroundStyle(DS.Colors.textPrimary)

                DS.Typography.headline(Text("Headline Text"))
                    .foregroundStyle(DS.Colors.textSecondary)

                DS.Typography.bodyRounded(Text("Body text with rounded design"))
                    .foregroundStyle(DS.Colors.textSecondary)

                DS.Typography.caption(Text("Caption text"))
                    .foregroundStyle(DS.Colors.textTertiary)

                DS.Typography.micro(Text("Micro Text"))
                    .foregroundStyle(DS.Colors.textMuted)
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(DS.Spacing.lg)

            // Cards showcase
            VStack(spacing: DS.Spacing.md) {
                Text("Elite Card")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .glassCard(tier: .elite)

                Text("Reliable Card")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .glassCard(tier: .reliable)

                Text("Unknown Card")
                    .padding()
                    .frame(maxWidth: .infinity)
                    .glassCard(tier: .unknown)
            }
            .padding(DS.Spacing.lg)

            // Skeleton loading
            SpotCardSkeleton()
                .padding(.horizontal, DS.Spacing.lg)
        }
    }
    .background(DS.Colors.backgroundPrimary)
}
