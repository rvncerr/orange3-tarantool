math.randomseed(os.time())

-- Correlation.
function orange_correlation(space_name)
    data = box.space[space_name]:select({})
    cols = #(box.space[space_name]:format())
    rows = #data

  mean = {}
  for i = 1,cols do
      mean[i] = 0
  end
  for i, v in ipairs(data) do
      for idx = 1,cols do
          if v[idx] ~= nil then
              mean[idx] = mean[idx] + v[idx]
          end
      end
  end
  for i = 1,cols do
      mean[i] = mean[i]/rows
  end

  sdev = {}
  for i = 1,cols do
      sdev[i] = 0
  end
  for i, v in ipairs(data) do
      for idx = 1,cols do
          if v[idx] ~= nil then
              sdev[idx] = sdev[idx] + math.pow(v[idx] - mean[idx], 2)
          end
      end
  end
  for i = 1,cols do
      sdev[i] = math.sqrt(sdev[i])
  end

  cov = {}
  for idx = 1, cols do
      cov[idx] = {}
      for jdx = 1, cols do
          cov[idx][jdx] = 0
      end
  end
  for i, v in ipairs(data) do
      for idx = 1,cols do
          for jdx = 1,cols do
              cov[idx][jdx] = cov[idx][jdx] + (v[idx] - mean[idx]) * (v[jdx] - mean[jdx])
          end
      end
  end

  corr = {}
  for idx = 1, cols do
      corr[idx] = {}
      for jdx = 1, cols do
          corr[idx][jdx] = cov[idx][jdx] / (sdev[idx] * sdev[jdx])
      end
  end

  return corr
end

-- PartialSelectWidget.
function orange_partial_select(space_name, index, probability)
    space = box.space[space_name]
    data = space:select({}, {index=index})
    partial_data = {}
    for _, tuple in ipairs(data) do
        if math.random() < probability then
            table.insert(partial_data, tuple)
        end
    end
    return partial_data
end
