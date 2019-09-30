from ROOT import *

tree1 = TTree("data", "test")
tree2 = TTree("data2", "test2")

c1 = TCanvas("c1", "c1", 1600, 1000)
c1.SetGrid()
gROOT.SetStyle("Plain")
gStyle.GetAttDate().SetTextColor(1)
gStyle.SetLabelFont(42, "XYZ")
gStyle.SetTextFont(42)
gStyle.SetTitleFont(42, "XYZ")
gStyle.SetStatH(0.12)
gStyle.SetStatW(0.15)
gStyle.SetOptFit(0)
gStyle.SetOptTitle(1)
gStyle.SetOptStat(0000)
gStyle.SetTitleFontSize(.05);
gStyle.SetLabelSize(.05, "XYZ");
gROOT.ForceStyle()
tree1.ReadFile("/home/dylan/Desktop/frame_slope.csv","x:z", ',');
tree2.ReadFile("/home/dylan/Desktop/foil_slope.csv","x:z", ',');

gr2 = TGraph()
gr1 = TGraph()
mg = TMultiGraph()


N = tree1.GetEntries()

for i in range(N):
    tree1.GetEntry(i)
    x1n,z1n= tree1.x, tree1.z
    gr1.SetPoint(gr1.GetN(), x1n, z1n)

M = tree2.GetEntries()

for i in range(M):
    tree2.GetEntry(i)
    x2n,z2n= tree2.x, tree2.z
    gr2.SetPoint(gr2.GetN(), x2n, z2n)



gr1.SetMarkerColor(1)
gr1.SetLineWidth(1)
gr1.SetMarkerStyle(20)
gr1.SetMarkerSize(1.2)

gr2.SetMarkerColor(4)
gr2.SetLineWidth(1)
gr2.SetMarkerStyle(20)
gr2.SetMarkerSize(1.2)


gr1.SetName("gr1")
gr1.SetTitle("X")


gr2.SetTitle("Y")
gr2.SetName("gr2")
gr2.Fit("x++1")
gr1.Fit("x++1")

mg.Add(gr1)
gr1.SetName("gr1")
gr1.SetTitle("Frame")
gr1.SetLineWidth(0)
mg.Add(gr2)
gr2.SetTitle("Foil")
gr2.SetName("gr2")


gr2.SetLineWidth(0)
mg.SetTitle(";X [mm];Z [mm]")


mg.Draw("ap")

c1.BuildLegend(0.1, 0.1, 0.2, 0.2)

c1.Update()
'''
gra = gr1.GetFunction("x++1")
grb = gr2.GetFunction("x++1")
p1 = [gra.GetParameter(0),gra.GetParError(0),gra.GetParameter(1),gra.GetParError(1)]
p2 = [grb.GetParameter(0),grb.GetParError(0),grb.GetParameter(1),grb.GetParError(1)]
print(p1, p2)
leg = TLegend(0.1, 0.1, 0.2, 0.2)
leg.SetTextSize(0.04)
for i in range(4):
    if i==0 :
        leg.AddEntry(gr1,"slope %.2f +- %.3f"%(p1[i], p1[i+1]),"l")
        leg.AddEntry(gr2,"slope %.2f +- %.3f"%(p2[i], p2[i+1]),"l")
    if i==2:
        leg.AddEntry(gr1,"z int %.2f +- %.3f"%(p1[i], p1[i+1]),"l")
        leg.AddEntry(gr2,"z int %.2f +- %.3f"%(p2[i], p2[i+1]),"l")


leg.Draw()


stats1 = gr1.GetListOfFunctions().FindObject("stats")
stats2 = gr2.GetListOfFunctions().FindObject("stats")
stats1.SetTextColor(kBlack)
stats2.SetTextColor(kBlue)
stats1.SetTextSize(0.04)
stats2.SetTextSize(0.04)
stats1.SetX1NDC(0.41)
stats1.SetX2NDC(0.65)
stats1.SetY1NDC(0.78)
stats1.SetY1NDC(0.88)
stats2.SetX1NDC(0.66)
stats2.SetX2NDC(0.90)
stats2.SetY1NDC(0.78)
stats2.SetY1NDC(0.88)
'''
c1.Modified()
c1.SaveAs("/home/dylan/slope.bmp");


