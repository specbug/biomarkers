//
//  ContentView.swift
//  biomarkers
//
//  Created by Rishit Vora on 29/11/23.
//

import SwiftUI
import Charts

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

struct WeeklyMetric: Identifiable {
	var id = UUID() // This property is required by the Identifiable protocol
	var date: Date
	var value: Double

	init(date: String, value: Double) {
		let dateFormatter = DateFormatter()
		dateFormatter.dateFormat = "yyyy-MM-dd"
		self.date = dateFormatter.date(from: date)!
		self.value = value
	}
}

// Function to generate dummy records
func generateDummyRecords() -> [WeeklyMetric] {
	var dummyData: [WeeklyMetric] = []
	let dateFormatter = DateFormatter()
	dateFormatter.dateFormat = "yyyy-MM-dd"

	for i in 1...7 {
		let randomValue = Int.random(in: 1...1000)
		let randomDate = Date().addingTimeInterval(TimeInterval(86400 * i)) // Adding 1 day interval
		let formattedDate = dateFormatter.string(from: randomDate)
		let dummyRecord = WeeklyMetric(date: formattedDate, value: Double(randomValue))
		dummyData.append(dummyRecord)
	}

	return dummyData
}

struct ActualChart: View {
	@State private var selectedPoint: WeeklyMetric? = nil
	@State private var tappedLocation: CGPoint?
	
	var data: [WeeklyMetric] = generateDummyRecords()
	
	private func findElement(location: CGPoint, proxy: ChartProxy, geometry: GeometryProxy) -> WeeklyMetric? {
			let relativeXPosition = location.x - geometry[proxy.plotAreaFrame].origin.x
			if let date = proxy.value(atX: relativeXPosition) as Date? {
				// Find the closest date element.
				var minDistance: TimeInterval = .infinity
				var index: Int? = nil
				for salesDataIndex in data.indices {
					let nthSalesDataDistance = data[salesDataIndex].date.distance(to: date)
					if abs(nthSalesDataDistance) < minDistance {
						minDistance = abs(nthSalesDataDistance)
						index = salesDataIndex
					}
				}
				if let index {
					return data[index]
				}
			}
			return nil
		}
	
	var body: some View {
		Chart(data) { monthlyData in
			LineMark(
				x: .value("Date", monthlyData.date),
				y: .value("Value", monthlyData.value)
			)
			.foregroundStyle(Color(hex: 0xff796c))
			.lineStyle(.init(lineWidth: 1.5))
			.symbol() {
				Circle()
					.strokeBorder(Color(hex: 0xff796c), lineWidth: 2)
					.background(Circle().foregroundColor(Color(.black)))
					.frame(width: 13)
			}
		}
		.frame(height: 150)
		.gridColumnAlignment(.center)
		.chartYAxis {
			AxisMarks(position: .leading, values: .automatic(desiredCount: 4)) { value in
				let yValue = value.as(Int.self)!
				AxisGridLine(stroke: StrokeStyle(lineWidth: 1, dash: [8.0, 6.0]))
					.foregroundStyle(Color(red: 120/255, green: 120/255, blue: 120/255, opacity: 0.8))
				AxisValueLabel() {
					Text("\(yValue)")
						.foregroundStyle(Color(red: 120/255, green: 120/255, blue: 120/255, opacity: 0.8))
				}
			}
		}
		.chartXAxis(.hidden)
		.chartOverlay { proxy in
			GeometryReader { geo in
				Rectangle().fill(.clear).contentShape(Rectangle())
					.gesture(
						SpatialTapGesture()
							.onEnded { value in
								let element = findElement(location: value.location, proxy: proxy, geometry: geo)
								if selectedPoint?.date == element?.date {
									// If tapping the same element, clear the selection.
									selectedPoint = nil
								} else {
									selectedPoint = element
								}
							}
							.exclusively(
								before: DragGesture()
									.onChanged { value in
										selectedPoint = findElement(location: value.location, proxy: proxy, geometry: geo)
									}
							)
					)
			}
		}
		.chartBackground { proxy in
					ZStack(alignment: .topLeading) {
						GeometryReader { geo in
							if true,
							   let selectedPoint {
								let dateInterval = Calendar.current.dateInterval(of: .day, for: selectedPoint.date)!
								let startPositionX1 = proxy.position(forX: dateInterval.start) ?? 0

								let lineX = startPositionX1 + geo[proxy.plotAreaFrame].origin.x
								let lineHeight = geo[proxy.plotAreaFrame].maxY
								let boxWidth: CGFloat = 50
								let boxOffset = max(0, min(geo.size.width - boxWidth, lineX - boxWidth / 2))

								Rectangle()
									.fill(Color(hex: 0xff796c, alpha: 0.25))
									.frame(width: 0.75, height: lineHeight)
									.position(x: lineX, y: lineHeight / 2)

								VStack(alignment: .center) {
									Text("\(selectedPoint.date, format: .dateTime.month().day())")
										.font(.custom("WorkSans-Regular", size: 10))
//										.foregroundStyle(Color(hex: 0xff796c))
										.foregroundStyle(Color(hex: 0x4c9ae8))
									Text("\(selectedPoint.value, format: .number)")
										.font(.custom("JetBrainsMono-Regular", size: 15))
										.foregroundColor(Color(hex: 0x8c8c8c))
									
								}
								.offset(x: boxOffset, y: -lineHeight/3.5)
							}
						}
					}
				}
		.padding()
	}
}



struct ActivityGrid: View {
	@State private var selectedCardIndex: Int? = nil
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
						favicon: Image(systemName: activityImages[index]),
						isSelected: selectedCardIndex == index
					)
						.background(selectedCardIndex == index ? Color.black : Color.white)
						.cornerRadius(25)
						.padding([index & 1 == 1 ? .horizontal : .leading, .bottom], 5)
						.shadow(color: Color.black.opacity(0.1), radius: 4, x: 0, y: 0)
						.onTapGesture {
							withAnimation {
								selectedCardIndex = selectedCardIndex == index ? nil : index
							}
						}
						.foregroundColor(selectedCardIndex == index ? .white : .black)
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
	var isSelected: Bool
	
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
			if isSelected {
				ActualChart()
			}
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

