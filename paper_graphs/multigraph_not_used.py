from ROOT import *

tree = TTree("data", "test")
c1 = TCanvas("c1", "c1", 200, 10, 700, 500)
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

#gStyle.SetImageScaling(3.)
gROOT.ForceStyle()
tree.ReadFile("1_16.csv","chi:theta:psi:phi:x:y:z:b:time:dot:resx:resy:a:c:mag1:mag2", ',');
mg = TMultiGraph()
gr2 = TGraph()
gr1 = TGraph()


N = tree.GetEntries()

for i in range(N):
    tree.GetEntry(i)

    xn, timen, yn = tree.x, tree.time, tree.y
    gr1.SetPoint(gr1.GetN(), timen, xn)
    gr2.SetPoint(gr2.GetN(), timen, yn)


gr1.SetMarkerColor(1)
gr1.SetLineWidth(4)
gr1.SetMarkerStyle(20)
gr1.SetMarkerSize(1)


gr2.SetMarkerColor(4)
gr2.SetLineWidth(4)
gr2.SetMarkerStyle(20)
gr2.SetMarkerSize(1)

mg.Add(gr1)
gr1.SetName("gr1")
gr1.SetTitle("test1")
gr1.SetLineWidth(3)
mg.Add(gr2)
gr2.SetTitle("test2")
gr2.SetName("gr2")

gr2.SetLineWidth(3)
mg.SetTitle("mult;time (min);distance (microns)")

mg.Draw("ap")
c1.BuildLegend()

c1.Update()
c1.Modified()
c1.SaveAs("/home/dylan/test.jpg");

import time
time.sleep(10)
