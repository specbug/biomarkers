//
//  ContentView.swift
//  biomarkers
//
//  Created by Rishit Vora on 29/11/23.
//

import SwiftUI

extension Color {
	init(hex: UInt, alpha: Double = 1) {
		self.init(
			.sRGB,
			red: Double((hex >> 16) & 0xff) / 255,
			green: Double((hex >> 08) & 0xff) / 255,
			blue: Double((hex >> 00) & 0xff) / 255,
			opacity: alpha
		)
	}
}


struct ContentView: View {
	
	var body: some View {
		VStack(spacing:0) {
			ProfileHeader()
			SegmentView()
			ActivityGrid()
		}
	}
}


struct SegmentView: View {
	// TODO: control views with selected segment, customise picker style
	@State private var selectedSegment = 0
	let segments = ["Metabolic", "Clinical"]
	
	var body: some View {
		VStack {
			Picker("Marker Source", selection: $selectedSegment) {
				ForEach(0..<segments.count) { index in
					Text(segments[index])
						.tag(index)
				}
			}
			.pickerStyle(SegmentedPickerStyle())
			.padding([.top, .horizontal], 10)
			.cornerRadius(25)
		}
	}
}



struct ProfileHeader: View {
	
	var body: some View {
		Image("the-purpose-of-technology")
			.resizable()
			.aspectRatio(contentMode: .fit)
			.overlay(
				RoundedRectangle(cornerRadius: 25)
					.stroke(Color(hex: 0xe5e5e5), lineWidth: 1)
				, alignment: .bottom
			)
	}
}

struct ActivityGrid: View {
	let columns: [GridItem] = [
			GridItem(.flexible(minimum: 80)),
			GridItem(.flexible(minimum: 80))
		]
	let activityTypes = ["Sleep", "Steps", "HR", "HRV", "MET", "VO2max"]
	let activityValues = [8.2, 12, 60, 57, 60, 37.5]
	let activityUnits = ["hrs", "k", "BPM", "ms", "hrs", "ml/kg/m"]
	let activityAggs = ["μ", "μ", "μ", "μ", "Σ", "μ"]
	let activityImages = ["bed.double.circle", "figure.walk.circle", "heart.circle", "arrow.clockwise.heart", "flame.circle", "timer.circle"]
	
	var body: some View {
		ScrollView {
			LazyVGrid(columns: columns, spacing: 10) {
				ForEach(activityTypes.indices, id: \.self) { index in
					MarkerCard(
						marker: Text(activityTypes[index]),
						agg: Text(activityAggs[index]),
						value: Text(String(activityValues[index])),
						unit: Text(activityUnits[index]),
						favicon: Image(systemName: activityImages[index])
					)
						.background(Color.white)
						.cornerRadius(25)
						.padding([index & 1 == 1 ? .horizontal : .leading, .bottom], 5)
						.shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 0)
				}
			}
			.padding(EdgeInsets(top: 10, leading: 5, bottom: 0, trailing: 5))
		}
	}
}

struct MarkerCard: View {
	var marker: Text
	var agg: Text
	var value: Text
	var unit: Text
	var favicon: Image
	
	var body: some View {
		VStack(spacing: 20) {
			CardHeader(header: marker, favicon: favicon)
				.frame(maxWidth: .infinity, alignment: .topLeading)
				.padding([.leading, .trailing], 20)
				.padding(.top, 15)
			CardContent(agg: agg, value: value, unit: unit)
				.frame(maxWidth: .infinity, alignment: .center)
				.padding(.bottom, 30)
				.padding(.top, 10)
		}
	}
}

struct CardHeader: View {
	var header: Text
	var favicon: Image
	
	var body: some View {
		HStack {
			header
				.font(.custom("WorkSans-Regular", size: 22))
				.fontWeight(.medium)
				.fontWidth(.compressed)
			Spacer()
			favicon
				.resizable()
				.frame(width: 18, height: 18)
				.foregroundColor(Color(hex: 0x4c9ae8))
		}
	}
}

struct CardContent: View {
	var agg: Text
	var value: Text
	var unit: Text
	
	var body: some View {
		HStack(alignment: .firstTextBaseline, spacing: 5) {
			agg
				.font(.custom("WorkSans-Regular", size: 14))
				.fontDesign(.monospaced)
				.foregroundColor(Color(hex: 0x8c8c8c))
			value
				.font(.custom("WorkSans-SemiBold", size: 26))
			unit
				.font(.custom("WorkSans-Regular", size: 15))
				.foregroundColor(Color(hex: 0x8c8c8c))
		}
	}
}

struct ContentView_Previews: PreviewProvider {
	static var previews: some View {
		ContentView()
			.background(Color(hex: 0xf7f9fb))
	}
}
