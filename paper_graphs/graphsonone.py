from ROOT import *

tree = TTree("data", "test")
c1 = TCanvas("c1", "c1", 1000, 1600)
c1.Divide(2, 4)
c1.SetGrid()
gROOT.SetStyle("Plain")
gStyle.GetAttDate().SetTextColor(1)
gStyle.SetLabelFont(132, "XYZ")
gStyle.SetTextFont(132)
gStyle.SetTitleFont(132, "XYZ")
gStyle.SetStatH(0.12)
gStyle.SetStatW(0.15)
gStyle.SetOptFit(0111)
gStyle.SetOptTitle(1)
gStyle.SetOptStat(0000)
gStyle.SetTitleFontSize(.05);
gStyle.SetLabelSize(.05, "XYZ");
#gStyle.SetImageScaling(3.)
gROOT.ForceStyle()
tree.ReadFile("/home/dylan/Desktop/long2.csv","chi:theta:psi:phi:x:y:z:b:mag1:mag2:time", ',');
gr2 = TGraph()
gr1 = TGraph()
gr3 = TGraph()
gr4 = TGraph()
gr5 = TGraph()
gr6 = TGraph()
gr7 = TGraph()


N = tree.GetEntries()

for i in range(N):
    tree.GetEntry(i)
    xn, timen, yn, thetan,phin, psin, zn, bn = tree.x, tree.time, tree.y, tree.theta, tree.phi, tree.psi, tree.z, tree.b
    gr1.SetPoint(gr1.GetN(), timen, xn)
    gr2.SetPoint(gr2.GetN(), timen, yn)
    gr3.SetPoint(gr2.GetN(), timen, zn)
    gr4.SetPoint(gr2.GetN(), timen, thetan)
    gr5.SetPoint(gr2.GetN(), timen, phin)
    gr6.SetPoint(gr2.GetN(), timen, psin)
    gr7.SetPoint(gr2.GetN(), timen, bn)


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
gr1.SetTitle("X")
gr1.SetLineWidth(1)

gr2.SetTitle("Y")
gr2.SetName("gr2")
gr2.SetLineWidth(1)


gr3.SetTitle("Z")
gr3.SetName("gr2")
gr3.SetLineWidth(3)

gr4.SetTitle("R1")
gr4.SetName("gr2")
gr4.SetLineWidth(3)

gr5.SetTitle("R2")
gr5.SetName("gr2")
gr5.SetLineWidth(3)

gr6.SetTitle("R3")
gr6.SetName("gr2")
gr6.SetLineWidth(3)

gr7.SetTitle("Deformation")
gr7.SetName("gr2")
gr7.SetLineWidth(3)


c1.cd(1)
gr1.Draw("ap1")
gr1.GetYaxis().SetTitle("#Delta X [microns]")
gr1.GetXaxis().SetTitle("time [hours]")
gr1.GetYaxis().SetTitleOffset(1.2)
gr1.GetYaxis().SetRangeUser(-150,150)

c1.cd(3)
gr2.Draw("ap1")
gr2.GetYaxis().SetTitle("#Delta Y [microns]")
gr2.GetXaxis().SetTitle("time [hours]")
gr2.GetYaxis().SetTitleOffset(1.2)
gr2.GetYaxis().SetRangeUser(-150,150)

c1.cd(5)
gr3.Draw("ap1")
gr3.GetYaxis().SetTitle("#Delta Z [microns]")
gr3.GetXaxis().SetTitle("time [hours]")
gr3.GetYaxis().SetTitleOffset(1.2)
gr3.GetYaxis().SetRangeUser(-150,150)


c1.cd(2)
gr4.Draw("ap1")
#gr4.GetYaxis().SetRangeUser(-6.55,-6.4)
gr4.GetYaxis().SetTitle("#Delta R1 [mrad]")
gr4.GetXaxis().SetTitle("time [hours]")
gr4.Draw("ap1")
gr4.GetYaxis().SetTitleOffset(1.3)


c1.cd(4)
gr5.Draw("ap1")
gr5.GetYaxis().SetTitle("#Delta R2 [mrad]")
gr5.GetXaxis().SetTitle("time [hours]")
gr5.GetYaxis().SetTitleOffset(1.3)

c1.cd(6)
gr6.Draw("ap1")
#gr6.GetYaxis().SetRangeUser(2.5,2.7)
gr6.GetYaxis().SetTitle("#Delta R3 [mrad]")
gr6.GetXaxis().SetTitle("time [hours]")
gr6.GetYaxis().SetTitleOffset(1.3)

c1.cd(7)
gr7.Draw("ap1")
gr7.GetYaxis().SetRangeUser(100,115)
gr7.GetYaxis().SetTitle("Deformation [microns]")
gr7.GetXaxis().SetTitle("time [hours]")
gr7.GetYaxis().SetTitleOffset(1.2)


#c1.BuildLegend()

c1.Update()
c1.Modified()
c1.SaveAs("/home/dylan/long.bmp");

