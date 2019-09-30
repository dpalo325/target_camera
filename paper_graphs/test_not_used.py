from ROOT import *

tree = TTree("data", "test")
c1 = TCanvas("c1", "c1", 1600, 1000)
gROOT.SetStyle("Plain")
gStyle.GetAttDate().SetTextColor(1)
gStyle.SetLabelFont(42, "XYZ")
gStyle.SetTextFont(42)
gStyle.SetTitleFont(42, "XYZ")
gStyle.SetStatH(0.12)
gStyle.SetStatW(0.15)
gStyle.SetOptFit(0)
gStyle.SetOptTitle(0)
gStyle.SetOptStat(0)
gStyle.SetLabelSize(.05, "X");
gStyle.SetLabelSize(.05, "Y");
#gStyle.SetImageScaling(3.)
gROOT.ForceStyle()

xygraph = TGraph()
tree.ReadFile("/home/dylan/Desktop/mag_linearity.csv","i:m:z", ',');


N = tree.GetEntries()

for i in range(N):
    tree.GetEntry(i)
    In, mn, zn = tree.i, tree.m, tree.z
    xygraph.SetPoint(xygraph.GetN(),mn , zn)


fout = TFile("output.root", "RECREATE")
gPad.SetLeftMargin(0.12)
gPad.SetBottomMargin(0.12)
xygraph.SetMarkerColor(1)
xygraph.SetLineWidth(4)
xygraph.SetMarkerStyle(20)
xygraph.SetMarkerSize(1)
xygraph.GetYaxis().SetTitleOffset(1.)
xygraph.GetYaxis().SetTitleOffset(1.)

xygraph.GetYaxis().SetTitleSize(0.055)
xygraph.GetXaxis().SetTitleSize(0.055)

#xygraph.SetTitle("Nominal Axial Distance - Magnification ")
xygraph.GetYaxis().SetTitle("Z [mm]")
xygraph.GetXaxis().SetTitle("Magnification []")
xygraph.Fit("x++1")


fout.cd()
c1.Write()
xygraph.Draw("AP")
xygraph.Write("Nominal Axial Distance - Magnification ")

fout.Write()
c1.SaveAs("/home/dylan/mag_linearity.pdf");

#import time
#time.sleep(10)
