'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/header';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import {
  HelpCircle,
  BookOpen,
  Calculator,
  TrendingUp,
  Lightbulb,
  Briefcase,
  FolderOpen,
  ExternalLink,
  Mail,
  MessageCircle,
  Search,
  ChevronRight,
} from 'lucide-react';
import Link from 'next/link';

const engines = [
  {
    id: 'engine1',
    title: 'Tax Incentive Calculator',
    icon: Calculator,
    color: 'blue',
    description:
      'Calculate tax credits and incentives across 25+ jurisdictions with cash flow projections and monetization analysis.',
    features: [
      'Multi-jurisdiction support (US, Canada, UK, Ireland, France, etc.)',
      'Automatic policy matching based on spend type',
      'Cash flow projection over 8 quarters',
      'Monetization options: Direct, Bank Loan, Broker Sale',
      'Effective rate calculation',
    ],
    link: '/dashboard/incentives',
  },
  {
    id: 'engine2',
    title: 'Waterfall Executor',
    icon: TrendingUp,
    color: 'green',
    description:
      'Execute waterfall distributions with IRR/NPV calculations and Monte Carlo simulations for risk analysis.',
    features: [
      'Industry-standard recoupment waterfall',
      'IRR calculation using Newton-Raphson method',
      'NPV with configurable discount rates',
      'Monte Carlo simulation (1,000 iterations)',
      'Stakeholder return analysis (P10/P50/P90)',
    ],
    link: '/dashboard/waterfall',
  },
  {
    id: 'engine3',
    title: 'Scenario Optimizer',
    icon: Lightbulb,
    color: 'purple',
    description:
      'Generate optimized capital stack scenarios with different objectives and comprehensive trade-off analysis.',
    features: [
      '5 scenario templates (Debt Heavy, Equity Heavy, Balanced, etc.)',
      'Multi-objective optimization',
      'Constraint validation',
      'Trade-off frontier analysis',
      'Strategic scoring integration (70% financial + 30% strategic)',
    ],
    link: '/dashboard/scenarios',
  },
  {
    id: 'engine5',
    title: 'Capital Programs',
    icon: Briefcase,
    color: 'amber',
    description:
      'Manage company-level capital vehicles with LP sources, portfolio constraints, and deployment tracking.',
    features: [
      '11 program types (External Fund, PE, Output Deal, SPV, etc.)',
      'Multi-source capital management',
      'Portfolio-level constraint validation',
      'Automatic source selection algorithm',
      'Deployment lifecycle tracking',
    ],
    link: '/dashboard/capital-programs',
  },
];

const faqs = [
  {
    question: 'How do I calculate tax incentives for my project?',
    answer:
      'Navigate to the Tax Incentive Calculator (Engine 1), enter your project details including budget and jurisdiction spends, then click Calculate. The system will automatically match applicable policies and compute your credits.',
  },
  {
    question: 'What is a waterfall distribution?',
    answer:
      'A waterfall distribution is the order in which film revenues are distributed to various stakeholders. It typically flows: Distribution Fees → Senior Debt → Gap Financing → Equity → Producer Corridor → Backend Participation.',
  },
  {
    question: 'How does the scenario optimizer work?',
    answer:
      'The scenario optimizer generates multiple capital stack configurations based on different objectives (maximize IRR, minimize risk, optimize tax capture). It then evaluates each scenario using our comprehensive scoring model.',
  },
  {
    question: 'What are Capital Programs?',
    answer:
      'Capital Programs represent company-level funding vehicles like external funds, output deals, or SPVs. They allow you to manage LP sources, set portfolio constraints, and track capital deployments across multiple projects.',
  },
  {
    question: 'How is the strategic score calculated?',
    answer:
      'Strategic scoring evaluates deal blocks across 4 dimensions: Ownership (IP retention), Control (creative approvals), Optionality (sequel rights, reversions), and Friction (execution complexity). The blended score combines 70% financial metrics with 30% strategic assessment.',
  },
  {
    question: 'Can I export results to Excel?',
    answer:
      'Export functionality is planned for a future release. Currently, you can copy data from tables or take screenshots of charts for external use.',
  },
  {
    question: 'How accurate are the Monte Carlo simulations?',
    answer:
      'Monte Carlo simulations run 1,000 iterations by default, providing P10/P50/P90 percentiles. Results are based on historical revenue distribution patterns and should be used as indicative ranges, not precise predictions.',
  },
  {
    question: 'What jurisdictions are supported?',
    answer:
      'We support 25+ jurisdictions including United States (Federal + States), Canada (Federal + Provinces), United Kingdom, Ireland, France, Germany, Australia, New Zealand, and more. New jurisdictions are added regularly.',
  },
];

export default function HelpPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredFaqs = faqs.filter(
    (faq) =>
      faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="flex flex-col">
      <Header
        title="Help Center"
        description="Documentation, guides, and frequently asked questions"
      />

      <div className="p-6 space-y-6">
        {/* Search */}
        <Card>
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search help topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Quick Links */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader className="pb-2">
              <BookOpen className="h-8 w-8 text-blue-500 mb-2" />
              <CardTitle className="text-lg">Getting Started</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                New to Film Financing Navigator? Start here.
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader className="pb-2">
              <HelpCircle className="h-8 w-8 text-purple-500 mb-2" />
              <CardTitle className="text-lg">Tutorials</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Step-by-step guides for each engine.
              </p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader className="pb-2">
              <ExternalLink className="h-8 w-8 text-green-500 mb-2" />
              <CardTitle className="text-lg">API Documentation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Technical reference for developers.
              </p>
              <a
                href="http://localhost:8000/api/v1/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-500 hover:underline mt-2 inline-block"
              >
                Open API Docs
              </a>
            </CardContent>
          </Card>

          <Card className="hover:shadow-md transition-shadow cursor-pointer">
            <CardHeader className="pb-2">
              <Mail className="h-8 w-8 text-amber-500 mb-2" />
              <CardTitle className="text-lg">Contact Support</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                Need help? Reach out to our team.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Engine Documentation */}
        <Card>
          <CardHeader>
            <CardTitle>Engine Documentation</CardTitle>
            <CardDescription>
              Learn about each calculation engine and its capabilities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-2">
              {engines.map((engine) => (
                <div
                  key={engine.id}
                  className={`p-4 border rounded-lg hover:shadow-md transition-shadow`}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`p-2 rounded-lg bg-${engine.color}-100`}
                      style={{
                        backgroundColor:
                          engine.color === 'blue'
                            ? '#dbeafe'
                            : engine.color === 'green'
                            ? '#dcfce7'
                            : engine.color === 'purple'
                            ? '#f3e8ff'
                            : '#fef3c7',
                      }}
                    >
                      <engine.icon
                        className={`h-5 w-5`}
                        style={{
                          color:
                            engine.color === 'blue'
                              ? '#2563eb'
                              : engine.color === 'green'
                              ? '#16a34a'
                              : engine.color === 'purple'
                              ? '#9333ea'
                              : '#d97706',
                        }}
                      />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold">{engine.title}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {engine.description}
                      </p>
                      <ul className="mt-3 space-y-1">
                        {engine.features.map((feature, idx) => (
                          <li
                            key={idx}
                            className="text-sm text-muted-foreground flex items-start gap-2"
                          >
                            <ChevronRight className="h-4 w-4 mt-0.5 flex-shrink-0" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                      <Link href={engine.link}>
                        <Button variant="link" className="mt-3 p-0 h-auto">
                          Open {engine.title}
                          <ChevronRight className="h-4 w-4 ml-1" />
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* FAQ */}
        <Card>
          <CardHeader>
            <CardTitle>Frequently Asked Questions</CardTitle>
            <CardDescription>Common questions and answers</CardDescription>
          </CardHeader>
          <CardContent>
            <Accordion type="single" collapsible className="w-full">
              {filteredFaqs.map((faq, index) => (
                <AccordionItem key={index} value={`item-${index}`}>
                  <AccordionTrigger className="text-left">
                    {faq.question}
                  </AccordionTrigger>
                  <AccordionContent className="text-muted-foreground">
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
            {filteredFaqs.length === 0 && (
              <p className="text-center text-muted-foreground py-8">
                No FAQs match your search query.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Glossary */}
        <Card>
          <CardHeader>
            <CardTitle>Key Terms Glossary</CardTitle>
            <CardDescription>Important financial and industry terminology</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              {[
                {
                  term: 'IRR (Internal Rate of Return)',
                  definition:
                    'The annualized effective compounded return rate that makes the net present value of all cash flows equal to zero.',
                },
                {
                  term: 'NPV (Net Present Value)',
                  definition:
                    'The difference between the present value of cash inflows and outflows over a period of time.',
                },
                {
                  term: 'Capital Stack',
                  definition:
                    'The hierarchy of financing sources used to fund a project, typically including debt, equity, and hybrid instruments.',
                },
                {
                  term: 'Waterfall',
                  definition:
                    'The predetermined order in which project revenues are distributed to various stakeholders.',
                },
                {
                  term: 'MFN (Most Favored Nations)',
                  definition:
                    'A clause ensuring a party receives terms at least as favorable as any other party in similar deals.',
                },
                {
                  term: 'Gap Financing',
                  definition:
                    'Debt financing secured against unsold distribution rights, bridging the gap between committed funds and budget.',
                },
                {
                  term: 'Soft Money',
                  definition:
                    'Non-repayable financing such as tax incentives, rebates, and grants.',
                },
                {
                  term: 'Backend Participation',
                  definition:
                    'A share of profits distributed after primary investors have recouped their investment.',
                },
              ].map((item, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <h4 className="font-medium text-sm">{item.term}</h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    {item.definition}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Support */}
        <Card>
          <CardHeader>
            <CardTitle>Need More Help?</CardTitle>
            <CardDescription>Get in touch with our support team</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button variant="outline">
                <Mail className="h-4 w-4 mr-2" />
                Email Support
              </Button>
              <Button variant="outline">
                <MessageCircle className="h-4 w-4 mr-2" />
                Live Chat
              </Button>
              <Button variant="outline">
                <BookOpen className="h-4 w-4 mr-2" />
                Read Documentation
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
