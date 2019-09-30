from ROOT import *

tree = TTree("data", "test")
c1 = TCanvas("c1", "c1", 1000, 1600)
c1.Divide(2, 3)
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
gStyle.SetLabelSize(.05, "XYZ");
#gStyle.SetImageScaling(3.)
gROOT.ForceStyle()
tree.ReadFile("/home/dylan/Desktop/fr3.csv","time:theta1:psi1:phi1:x1:y1:z1:theta2:psi2:phi2:x2:y2:z2", ',');
gr2 = TGraph()
gr1 = TGraph()
gr3 = TGraph()
gr4 = TGraph()
gr5 = TGraph()
gr6 = TGraph()
gr7 = TGraph()
gr8 = TGraph()
gr9 = TGraph()
gr10 = TGraph()
gr11 = TGraph()
gr12 = TGraph()
mg1 = TMultiGraph()
mg2 = TMultiGraph()
mg3 = TMultiGraph()
mg4 = TMultiGraph()
mg5 = TMultiGraph()
mg6 = TMultiGraph()


N = tree.GetEntries()

for i in range(N):
    tree.GetEntry(i)
    xn, timen, yn, thetan,phin, psin, zn, x2n, y2n, z2n, theta2n, phi2n, psi2n = tree.x1, tree.time, tree.y1, \
    tree.theta1, tree.phi1, tree.psi1, tree.z1,tree.x2, tree.y2, tree.z2, tree.theta2, tree.phi2, tree.psi2
    gr1.SetPoint(gr1.GetN(), timen, xn)
    gr2.SetPoint(gr2.GetN(), timen, yn)
    gr3.SetPoint(gr3.GetN(), timen, zn)
    gr4.SetPoint(gr4.GetN(), timen, thetan)
    gr5.SetPoint(gr5.GetN(), timen, phin)
    gr6.SetPoint(gr6.GetN(), timen, psin)
    gr7.SetPoint(gr7.GetN(), timen, x2n)
    gr8.SetPoint(gr8.GetN(), timen, y2n)
    gr9.SetPoint(gr9.GetN(), timen, z2n)
    gr10.SetPoint(gr10.GetN(), timen, theta2n)
    gr11.SetPoint(gr11.GetN(), timen, phi2n)
    gr12.SetPoint(gr12.GetN(), timen, psi2n)


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

gr7.SetMarkerColor(4)
gr7.SetLineWidth(1)
gr7.SetMarkerStyle(21)
gr7.SetMarkerSize(0.8)

gr8.SetMarkerColor(4)
gr8.SetLineWidth(1)
gr8.SetMarkerStyle(20)
gr8.SetMarkerSize(0.8)
gr9.SetMarkerColor(4)
gr9.SetLineWidth(4)
gr9.SetMarkerStyle(20)
gr9.SetMarkerSize(0.8)

gr10.SetMarkerColor(4)
gr10.SetLineWidth(4)
gr10.SetMarkerStyle(20)
gr10.SetMarkerSize(0.8)

gr11.SetMarkerColor(4)
gr11.SetLineWidth(4)
gr11.SetMarkerStyle(20)
gr11.SetMarkerSize(0.8)
gr12.SetMarkerColor(4)
gr12.SetLineWidth(4)
gr12.SetMarkerStyle(20)
gr12.SetMarkerSize(0.8)



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




c1.cd(1)
mg1.Add(gr1)
gr1.SetName("X1")
gr1.SetTitle("X1")
gr1.SetLineWidth(0)
gr1.GetYaxis().SetTitle("#Delta X [microns]")
gr1.GetXaxis().SetTitle("time [hours]")
gr1.GetYaxis().SetTitleOffset(1.2)
mg1.Add(gr7)
gr7.SetTitle("X2")
gr7.SetName("X2")
mg1.Draw("ap")


c1.cd(3)
mg2.Add(gr2)
gr2.SetName("Y1")
gr2.SetTitle("X1")
gr2.SetLineWidth(0)
gr2.GetYaxis().SetTitle("#Delta X [microns]")
gr2.GetXaxis().SetTitle("time [hours]")
gr2.GetYaxis().SetTitleOffset(1.2)
mg2.Add(gr8)
gr8.SetTitle("X2")
gr8.SetName("X2")
mg2.Draw("ap")

c1.cd(5)
mg3.Add(gr3)
gr3.SetName("Y1")
gr3.SetTitle("X1")
gr3.SetLineWidth(0)
gr3.GetYaxis().SetTitle("#Delta X [microns]")
gr3.GetXaxis().SetTitle("time [hours]")
gr3.GetYaxis().SetTitleOffset(1.2)
mg3.Add(gr9)
gr9.SetTitle("X2")
gr9.SetName("X2")
mg3.Draw("ap")

c1.cd(2)
mg4.Add(gr4)
gr4.SetName("Y1")
gr4.SetTitle("X1")
gr4.SetLineWidth(0)
gr4.GetYaxis().SetTitle("#Delta X [microns]")
gr4.GetXaxis().SetTitle("time [hours]")
gr4.GetYaxis().SetTitleOffset(1.2)
mg4.Add(gr10)
gr10.SetTitle("X2")
gr10.SetName("X2")
mg4.Draw("ap")


c1.cd(4)
mg5.Add(gr5)
gr5.SetName("Y1")
gr5.SetTitle("X1")
gr5.SetLineWidth(0)
gr5.GetYaxis().SetTitle("#Delta X [microns]")
gr5.GetXaxis().SetTitle("time [hours]")
gr5.GetYaxis().SetTitleOffset(1.2)
mg5.Add(gr11)
gr11.SetTitle("X2")
gr11.SetName("X2")
mg5.Draw("ap")

c1.cd(6)
mg6.Add(gr6)
gr6.SetName("Y1")
gr6.SetTitle("X1")
gr6.SetLineWidth(0)
gr6.GetYaxis().SetTitle("#Delta X [microns]")
gr6.GetXaxis().SetTitle("time [hours]")
gr6.GetYaxis().SetTitleOffset(1.2)
mg6.Add(gr12)
gr12.SetTitle("X2")
gr12.SetName("X2")
mg6.Draw("ap")



mg1.SetTitle(";Time [hours];#Delta Z [#mum]")

c1.BuildLegend(0.1, 0.1, 0.3, 0.3)

c1.Update()
c1.Modified()
c1.SaveAs("/home/dylan/frame.bmp");

