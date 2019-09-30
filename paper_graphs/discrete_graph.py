from ROOT import *

tree = TTree("data", "test")
tree2 = TTree("data2", "test2")

c1 = TCanvas("c1", "c1", 2000, 1000)

c1.Divide(4, 2,0.0001,0.0001)


c1.SetGrid()
gROOT.SetStyle("Plain")
gStyle.GetAttDate().SetTextColor(1)
gStyle.SetLabelFont(42, "XYZ")
gStyle.SetTextFont(42)
gStyle.SetTitleFont(42, "XYZ")
gStyle.SetStatH(0.12)
gStyle.SetStatW(0.15)
gStyle.SetOptFit(0111)
gStyle.SetOptTitle(1)
gStyle.SetOptStat(0000)
gStyle.SetTitleFontSize(.05);
gStyle.SetLabelSize(.055, "XYZ");

gStyle.SetTitleY(0.95)
gStyle.SetTitleX(0.13)

#gStyle.SetImageScaling(3.)
gROOT.ForceStyle()
tree.ReadFile("/home/dylan/Downloads/discrete_5_20.csv","time:theta:phi:psi:x:y:z:b", ',');
tree2.ReadFile("/home/dylan/Downloads/discretetranslations.csv","time2:x2:y2:z2", ',');

gr2 = TGraph()
gr1 = TGraph()
gr3 = TGraph()
gr4 = TGraph()
gr5 = TGraph()
gr6 = TGraph()
gr7 = TGraph()

N = tree.GetEntries()
M = tree2.GetEntries()


for i in range(M):
    tree2.GetEntry(i)
    xn, timen, yn, zn = tree2.x2, tree2.time2, tree2.y2, tree2.z2
    gr1.SetPoint(gr1.GetN(), timen, xn)
    gr2.SetPoint(gr2.GetN(), timen, yn)
    gr3.SetPoint(gr2.GetN(), timen, zn)
    #gr4.SetPoint(gr2.GetN(), timen, phin)
    #gr5.SetPoint(gr2.GetN(), timen, thetan)
    #gr6.SetPoint(gr2.GetN(), timen, psin)
    #gr7.SetPoint(gr2.GetN(), timen, bn)


for i in range(N):
    tree.GetEntry(i)
    timen, thetan,phin, psin, bn = tree.time, tree.theta, tree.phi, tree.psi, tree.b
    #gr1.SetPoint(gr1.GetN(), timen, xn)
    #gr2.SetPoint(gr2.GetN(), timen, yn)
    #gr3.SetPoint(gr2.GetN(), timen, zn)
    gr4.SetPoint(gr4.GetN(), timen, phin)
    gr5.SetPoint(gr4.GetN(), timen, thetan)
    gr6.SetPoint(gr4.GetN(), timen, psin)
    gr7.SetPoint(gr4.GetN(), timen, bn)


gr1.SetMarkerColor(1)
gr1.SetLineWidth(1)
gr1.SetMarkerStyle(20)
gr1.SetMarkerSize(0.8)

gr2.SetMarkerColor(1)
gr2.SetLineWidth(1)
gr2.SetMarkerStyle(20)
gr2.SetMarkerSize(0.8)
gr3.SetMarkerColor(1)
gr3.SetLineWidth(4)
gr3.SetMarkerStyle(20)
gr3.SetMarkerSize(0.8)

gr4.SetMarkerColor(1)
gr4.SetLineWidth(4)
gr4.SetMarkerStyle(20)
gr4.SetMarkerSize(0.8)

gr5.SetMarkerColor(1)
gr5.SetLineWidth(4)
gr5.SetMarkerStyle(20)
gr5.SetMarkerSize(0.8)
gr6.SetMarkerColor(1)
gr6.SetLineWidth(4)
gr6.SetMarkerStyle(20)
gr6.SetMarkerSize(0.8)

gr7.SetMarkerColor(1)
gr7.SetLineWidth(4)
gr7.SetMarkerStyle(20)
gr7.SetMarkerSize(0.8)


gr1.SetName("gr1")
gr1.SetTitle("")
gr1.SetLineWidth(1)

gr2.SetTitle("")
gr2.SetName("gr2")
gr2.SetLineWidth(1)


gr3.SetTitle("")
gr3.SetName("gr2")
gr3.SetLineWidth(3)

gr4.SetTitle("")
gr4.SetName("gr2")
gr4.SetLineWidth(3)

gr5.SetTitle("")
gr5.SetName("gr2")
gr5.SetLineWidth(3)

gr6.SetTitle("")
gr6.SetName("gr2")
gr6.SetLineWidth(3)

gr7.SetTitle("")
gr7.SetName("gr2")
gr7.SetLineWidth(3)

c1.cd(1)
gPad.Range(0,0,100, 100)
gPad.SetBottomMargin(0.13)
gPad.SetTopMargin(0.05)
gPad.SetLeftMargin(0.18)
gPad.SetRightMargin(0.02)

gr1.Draw("ap1")
gr1.GetYaxis().SetTitle("#Delta X^{C} [#mum]")
gr1.GetXaxis().SetTitle("Time [hours]")
gr1.GetYaxis().SetTitleOffset(1.2)
gr1.GetYaxis().SetTitleSize(0.067)
gr1.GetXaxis().SetRangeUser(0,4.5)

gr1.GetYaxis().SetRangeUser(-10,150)
gr1.GetXaxis().SetTitleOffset(0.9)
gr1.GetXaxis().SetTitleSize(0.067)
line = TLine(1.3, -10, 1.3, 150)
line.SetLineColor(kRed);
line.Draw();

#line5 = TLine(4.7, -150, 4.7, 150)
#line5.SetLineColor(kRed)
#line5.Draw()

c1.cd(2)
gPad.SetBottomMargin(0.13)
gPad.SetTopMargin(0.05)
gPad.SetLeftMargin(0.18)
gPad.SetRightMargin(0.02)

gr2.Draw("ap1")
gr2.GetYaxis().SetTitle("#Delta Y^{C} [#mum]")
gr2.GetXaxis().SetTitle("Time [hours]")
gr2.GetYaxis().SetTitleOffset(1.2)
gr2.GetYaxis().SetTitleSize(0.067)
gr2.GetYaxis().SetRangeUser(-10,50)
gr2.GetXaxis().SetTitleOffset(0.9)
gr2.GetXaxis().SetTitleSize(0.067)
gr2.GetXaxis().SetRangeUser(0,4.5)
line2 = TLine(1.3, -10, 1.3, 50)
line2.SetLineColor(kRed)
line2.Draw()
c1.cd(3)
gPad.SetBottomMargin(0.13)
gPad.SetTopMargin(0.05)
gPad.SetLeftMargin(0.18)
gPad.SetRightMargin(0.02)

gr3.Draw("ap1")
gr3.GetYaxis().SetTitle("#Delta Z^{C} [#mum]")
gr3.GetXaxis().SetTitle("Time [hours]")
gr3.GetYaxis().SetTitleOffset(1.2)
gr3.GetYaxis().SetTitleSize(0.067)
gr3.GetYaxis().SetRangeUser(-130,130)
gr3.GetXaxis().SetTitleOffset(0.9)
gr3.GetXaxis().SetTitleSize(0.067)
gr3.GetXaxis().SetRangeUser(0,4.5)
line3 = TLine(1.3, -130, 1.3,130)
line3.SetLineColor(kRed)
line3.Draw()

c1.cd(5)
gPad.SetBottomMargin(0.13)
gPad.SetTopMargin(0.05)
gPad.SetLeftMargin(0.18)
gPad.SetRightMargin(0.02)

gr4.Draw("ap1")
gr4.GetYaxis().SetRangeUser(-0.2,0.1)
gr4.GetYaxis().SetTitle("#Delta #phi [mrad]")
gr4.GetXaxis().SetTitle("Time [hours]")
gr4.Draw("ap1")
gr4.GetYaxis().SetTitleOffset(1.2)
gr4.GetYaxis().SetTitleSize(0.067)
gr4.GetXaxis().SetTitleOffset(0.9)
gr4.GetXaxis().SetTitleSize(0.067)
gr4.GetXaxis().SetRangeUser(0,4.5)
line4 = TLine(1.3, -0.2, 1.3, 0.1)
line4.SetLineColor(kRed)
line4.Draw()

c1.cd(6)
gPad.SetBottomMargin(0.13)
gPad.SetTopMargin(0.05)
gPad.SetLeftMargin(0.18)
gPad.SetRightMargin(0.02)

gr5.Draw("ap1")
gr5.GetXaxis().SetRangeUser(0,4.5)
gr5.GetYaxis().SetRangeUser(-0.1,0.1)

gr5.GetYaxis().SetTitle("#Delta #theta [mrad]")
gr5.GetXaxis().SetTitle("Time [hours]")
gr5.GetYaxis().SetTitleOffset(1.3)
gr5.GetYaxis().SetTitleSize(0.067)
gr5.GetXaxis().SetTitleOffset(0.9)
gr5.GetXaxis().SetTitleSize(0.067)
line5 = TLine(1.3, -0.1, 1.3, 0.1)
line5.SetLineColor(kRed)
line5.Draw()

c1.cd(7)
gPad.SetBottomMargin(0.13)
gPad.SetTopMargin(0.05)
gPad.SetLeftMargin(0.18)
gPad.SetRightMargin(0.02)

gr6.Draw("ap1")
gr6.GetYaxis().SetRangeUser(-0.1,0.2)
gr6.GetYaxis().SetTitle("#Delta #psi [mrad]")
gr6.GetXaxis().SetTitle("Time [hours]")
gr6.GetYaxis().SetTitleOffset(1.3)
gr6.GetYaxis().SetTitleSize(0.067)
gr6.GetXaxis().SetTitleOffset(0.9)
gr6.GetXaxis().SetTitleSize(0.067)
gr6.GetXaxis().SetRangeUser(0,4.5)
line8 = TLine(1.3, -0.1, 1.3, 0.2)
line8.SetLineColor(kRed)
line8.Draw()

c1.cd(4)
gPad.SetBottomMargin(0.13)
gPad.SetTopMargin(0.05)
gPad.SetLeftMargin(0.18)
gPad.SetRightMargin(0.02)
gr7.GetYaxis().SetRangeUser(60,80)

gr7.Draw("ap1")
gr7.GetYaxis().SetTitle("Deformation [#mum]")
gr7.GetXaxis().SetTitle("Time [hours]")
gr7.GetYaxis().SetTitleOffset(1.2)
gr7.GetXaxis().SetTitleOffset(0.9)
gr7.GetXaxis().SetTitleSize(0.067)
gr7.GetYaxis().SetTitleSize(0.067)
gr7.GetYaxis().SetTitleSize(0.067)
gr7.GetXaxis().SetRangeUser(0,4.5)
line6 = TLine(1.3, 60, 1.3, 80)
line6.SetLineColor(kRed)
line6.Draw()

#c1.BuildLegend()

c1.Update()
c1.Modified()
c1.SaveAs("/home/dylan/discrete.pdf");

