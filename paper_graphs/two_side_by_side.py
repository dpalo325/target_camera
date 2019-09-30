from ROOT import *

tree = TTree("data", "test")
c1 = TCanvas("c1", "c1", 700, 500)

c1.Divide(1, 2,0.01,0.01)


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
gStyle.SetOptStat(1111)
gStyle.SetTitleFontSize(.1);
gStyle.SetLabelSize(.1, "X");
gStyle.SetLabelSize(.1, "Y");

gStyle.SetTitleY(0.95)
gStyle.SetTitleX(0.18)

#gStyle.SetImageScaling(3.)
gROOT.ForceStyle()
#tree.ReadFile("/home/dylan/Downloads/mag.csv","time:mag1:mag2", ',');
tree.ReadFile("/home/dylan/Downloads/t_zc_zc2_dzc.csv","time:zc1:zc2:relzc", ',');

gr2 = TGraph()
gr1 = TGraph()



N = tree.GetEntries()

for i in range(N):
    tree.GetEntry(i)
    xn, timen, yn = tree.zc1*1000, tree.time, tree.relzc
    gr1.SetPoint(gr1.GetN(), timen, xn)
    gr2.SetPoint(gr2.GetN(), timen, yn)


gr1.SetMarkerColor(1)
gr1.SetLineWidth(1)
gr1.SetMarkerStyle(20)
gr1.SetMarkerSize(0.8)

gr2.SetMarkerColor(1)
gr2.SetLineWidth(1)
gr2.SetMarkerStyle(20)
gr2.SetMarkerSize(0.8)

gr1.SetName("gr1")
gr1.SetTitle("")
gr1.SetLineWidth(1)
gr2.SetName("gr1")

gr2.SetTitle("")
gr2.SetLineWidth(1)


c1.cd(1)
gPad.Range(0,0,100, 100)
gPad.SetBottomMargin(0.18)
gPad.SetTopMargin(0.07)
gPad.SetLeftMargin(0.12)
gPad.SetRightMargin(0.02)

gr1.Draw("ap1")
gr1.GetYaxis().SetTitle("#Delta Z^{C} [#mum]")
gr1.GetXaxis().SetTitle("Time [hours]")
gr1.GetYaxis().SetTitleOffset(0.6)
gr1.GetYaxis().SetTitleSize(0.1)
#gr1.GetXaxis().SetRangeUser(0,80)
gr1.GetXaxis().SetNdivisions(505)
gr1.GetYaxis().SetNdivisions(505)

gr1.GetYaxis().SetRangeUser(-200,200)
gr1.GetXaxis().SetTitleOffset(0.9)
gr1.GetXaxis().SetTitleSize(0.1)
#line = TLine(0, -150, 1.3, 150)
#line.SetLineColor(kRed);
#line.Draw();

line5 = TLine(60, 4.085, 60, 4.295)
line5.SetLineColor(kRed)
#line5.Draw()

c1.cd(2)
gPad.SetBottomMargin(0.18)
gPad.SetTopMargin(0.07)
gPad.SetLeftMargin(0.12)
gPad.SetRightMargin(0.02)

gr2.Draw("ap1")
line2 = TLine(60, -0.2, 60, 0.445)
line2.SetLineColor(kRed)
#line2.Draw()
gr2.GetYaxis().SetTitle("#Delta Z^{C}_{Min} - #Delta Z^{C}_{Indep} [#mum]")
gr2.GetXaxis().SetTitle("Time [hours]")
gr2.GetYaxis().SetTitleOffset(0.6)
gr2.GetYaxis().SetTitleSize(0.1)
gr2.GetYaxis().SetRangeUser(-250,250)
gr2.GetXaxis().SetTitleOffset(0.9)
gr2.GetXaxis().SetTitleSize(0.1)
gr2.GetXaxis().SetNdivisions(505);
gr2.GetYaxis().SetNdivisions(505);



c1.Update()
c1.Modified()
c1.SaveAs("/home/dylan/indepz2.pdf");

